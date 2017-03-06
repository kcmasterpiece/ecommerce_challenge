from datetime import datetime, timedelta, time
from django.test import TestCase
from django.db import connection
from django.db.models import Sum
from django.utils import timezone
import json
import pytz
from api.models import Customers, Products, Categories, Orders, OrderItems, ProductCategories
from api.businessLogic import OrderMethods
from api.queryHelper import QueryHelper
import generate_data
# Create your tests here.

class DataModelTest(TestCase):
    def test_can_create_customer(self):
        """Tests that customers can be created"""
        customer = Customers.objects.create(first_name='Bob',last_name='Smith')
        saved_customers = Customers.objects.all()
        self.assertEqual(saved_customers[0].customerId, customer.customerId)
         
    def test_can_create_product(self):
        """Tests that products can be created"""
        product = Products.objects.create(name='MacBook Pro', price='1999.00')
        saved_products = Products.objects.all()
        self.assertEqual(saved_products[0].productId, product.productId)

    def test_can_create_category(self):
        """Tests that categories can be created"""
        category = Categories.objects.create(name='Computers')
        saved_categories = Categories.objects.all()
        self.assertEqual(saved_categories[0].categoryId, category.categoryId)
    
    def test_can_create_productcategories(self):
        """Tests that product categories can be created"""
        category = Categories.objects.create(name='Computers')
        product = Products.objects.create(name='MacBook Pro', price='1999.00')
        productCategory = ProductCategories.objects.create(category=category, product=product)
        saved_productCategories = ProductCategories.objects.all()
        self.assertEqual(saved_productCategories[0].productCategoryId, productCategory.productCategoryId)
    
    # def test_perform_query(self):
    def test_products_categories_many_to_many(self):
        """Tests that products and categories have a many to many relationship
        """
        products = [ Products.objects.create(name='13 inch MacBook Pro', price='1799.00'),
                  Products.objects.create(name='15 inch MacBook Pro', price='1999.00'),
                  Products.objects.create(name='17 inch MacBook Pro', price='2199.00') ]
        categories = [Categories.objects.create(name='Computers'),
                      Categories.objects.create(name='Laptops')]

        for p in products:
            for c in categories:
                ProductCategories.objects.create(category=c, product=p)

        saved_productCategories = ProductCategories.objects.all()
        self.assertEqual(set(products), set(x.product for x in saved_productCategories))
        self.assertEqual(set(categories), set(x.category for x in saved_productCategories))
        self.assertEqual(len(categories)*len(products), len(saved_productCategories))
    
    def test_can_create_orders(self):
        """Tests that orders can be created"""
        items = [Products.objects.create(name='13 inch MacBook Pro', price='1799.00'),
                 Products.objects.create(name='15 inch MacBook Pro', price='1999.00'),
                 Products.objects.create(name='17 inch MacBook Pro', price='2199.00')]
        customer = Customers.objects.create(first_name='Bob',last_name='Smith')
        orderTotal = sum(float(p.price) for p in items)
        order = Orders.objects.create(orderTotal = orderTotal, customer=customer)

        for p in items:
            orderItem = OrderItems.objects.create(product=p, productName=p.name, price=p.price, quantity=1, order=order)
            
        # Test order items match
        saved_orderItems = OrderItems.objects.filter(order=order)
        for i in range(0, len(saved_orderItems)):
            self.assertEqual(saved_orderItems[i].product.productId, items[i].productId, "Order Item product id {oi} is not equal to product id {pid}".format(pid=items[i].productId, oi=saved_orderItems[i].product))
        
        # Test order matches
        saved_orders = Orders.objects.all()
        self.assertEqual(saved_orders[0].orderId, order.orderId)

    def test_all_statuses_are_available(self):
        """Tests that all order statuses are available for use"""
        statuses = set(['waiting for delivery','on its way', 'delivered'])
        orderStatuses = set([d for (v, d) in Orders._meta.get_field('orderStatus').choices])
        self.assertEquals(statuses, orderStatuses)

    def test_orders_can_have_a_status(self):
        """Tests that orders can have a status"""
        items = [Products.objects.create(name='13 inch MacBook Pro', price='1799.00'),
                 Products.objects.create(name='15 inch MacBook Pro', price='1999.00'),
                 Products.objects.create(name='17 inch MacBook Pro', price='2199.00')]
        order = OrderMethods.createOrder(items, first_name='Bob', last_name='Smith')
        orderStatuses = set([d for (v, d) in Orders._meta.get_field('orderStatus').choices])
        self.assertIn(order.get_orderStatus_display(), orderStatuses)

    def test_customer_can_have_many_orders(self):
        """Tests that a customer can have many orders"""
        customer = Customers.objects.create(first_name='Bob',last_name='Smith') 
        items = [Products.objects.create(name='13 inch MacBook Pro', price='1799.00'),
                 Products.objects.create(name='15 inch MacBook Pro', price='1999.00'),
                 Products.objects.create(name='17 inch MacBook Pro', price='2199.00')]
        OrderMethods.createOrder(items, customer=customer) 
        OrderMethods.createOrder(items, customer=customer) 

        self.assertGreater(len(Orders.objects.filter(customer=customer)), 1)

class LogicTest(TestCase):
    def test_businessLogic_orders_creates_orders(self):
        """Tests api/businessLogic OrderMethods.createOrder() creates orders"""
        items = [Products.objects.create(name='13 inch MacBook Pro', price='1799.00'),
                 Products.objects.create(name='15 inch MacBook Pro', price='1999.00'),
                 Products.objects.create(name='17 inch MacBook Pro', price='2199.00')]
        # create order manually
        customer = Customers.objects.create(first_name='Bob',last_name='Smith')
        orderTotal = sum(float(p.price) for p in items)
        order = Orders.objects.create(orderTotal = orderTotal, customer=customer)
        for p in items:
            orderItem = OrderItems.objects.create(product=p, productName=p.name, price=p.price, quantity=1, order=order)
        order = OrderMethods.createOrder(items, customer=customer)

        # Test order matches
        saved_orders = Orders.objects.all()
        
        # Check customer matches
        self.assertEqual(saved_orders[0].customer, order.customer)
        
        # Check order total matches
        self.assertEqual(saved_orders[0].orderTotal, order.orderTotal)

        # Check order products match (items won't match as id's will be different)
        orderProducts = lambda orderItems: [oi.product for oi in orderItems]
        self.assertEqual(set(orderProducts(OrderItems.objects.filter(order=order))),
                         set(orderProducts(OrderItems.objects.filter(order=saved_orders[0])))
                         )


class QueryTest(TestCase):
    @classmethod
    def setUpClass(self):
        super(QueryTest, self).setUpClass()
        generate_data.main()

    def test_order_method_number_purchased_by_customer_by_category(self):
        """Tests that sql query in question 3 and orm solution in question 4 match"""
        cursor = connection.cursor()
        query = '''
            SELECT customerId as 'order__customer_id', first_name as 'order__customer__first_name', categoryId as 'product__productcategories__category__categoryId',
                c.name as 'product__productcategories__category__name', sum(oi.quantity) as 'number_purchased'  
            FROM api_customers cus 
            INNER JOIN api_orders o on o.customer_id = cus.customerId 
            INNER JOIN api_orderItems oi  on oi.order_id = o.orderId 
            INNER JOIN api_products p   on p.productId = oi.product_id 
            INNER JOIN api_productcategories pc  on p.productId = pc.product_id 
            INNER JOIN api_categories c  on pc.category_id = c.categoryId 
            GROUP BY customerId, first_name, categoryId, c.name; '''
        cursor.execute(query)
        results = QueryHelper.dictfetchall(cursor)
        ormResults = OrderMethods.number_purchased_by_customer_and_category()
        # since raw query returns value as 'Decimal('n')', convert values
        for i in range(0,len(results)):
            results[i]['number_purchased'] = int(results[i]['number_purchased'])
        
        for row in ormResults:
            self.assertIn(row, results)    

class ViewsTest(TestCase):
    @classmethod
    def setUpClass(self):
        super(ViewsTest, self).setUpClass()
        generate_data.main()

    def test_api_returns_orders_for_customer(self):
        """Tests that the api returns orders for a particular customer"""

        c = Customers.objects.all()
        orders = Orders.objects.filter(customer=c[0])
        response = self.client.get('/api/customers/orders/' + str(c[0].customerId))
        header, header_value = response._headers['content-type'] 
        jsonResponse = json.loads(response.content)

        self.assertEquals(header_value, 'application/json')
        self.assertEquals(c[0].customerId, jsonResponse['customer']['customerId'])
        self.assertEquals(len(orders), len(jsonResponse['orders']))

    def test_api_returns_product_sales_by_period_week(self):
        """Tests that the api returns product sales by in a particular week"""
        urldf = '%m-%d-%Y'
        dateToCheck = Orders.objects.all().values('orderDate')[0]['orderDate']
        midnight = time(0)
        sd = timezone.make_aware(datetime.combine(dateToCheck.date(), midnight), pytz.timezone('UTC'), is_dst=False)
        # set date to Sunday aka beginning of week
        sd = (sd + timedelta(days=0-int(dateToCheck.strftime('%w'))))
        ed = (sd + timedelta(weeks=1))
        test_url = '/api/reporting/products/sales?startdate={sd}&enddate={ed}&interval=week'.format(
                sd=sd.strftime(urldf),
                ed=ed.strftime(urldf))
        response = self.client.get(test_url)
        oi = OrderItems.objects.filter(order__orderDate__range=[sd,ed]).values('product_id')\
                .annotate(quantity_sold=Sum('quantity'), product_sales_revenue=Sum('price'))
        body = json.loads(response.content)
        for r in body['results']:
            qs = oi.filter(product_id=r['product_id']).values('quantity_sold')
            ps = oi.filter(product_id=r['product_id']).values('product_sales_revenue')
            self.assertEquals(int(r['quantity_sold']), qs[0]['quantity_sold'])
            self.assertEquals(float(r['product_sales_revenue']), float(ps[0]['product_sales_revenue']))

    def test_api_returns_product_sales_by_period_day(self):
        """Tests that the api returns product sales by in a particular day"""
        urldf = '%m-%d-%Y'
        dateToCheck = Orders.objects.all().values('orderDate')[0]['orderDate']
        midnight = time(0)
        sd = timezone.make_aware(datetime.combine(dateToCheck.date(), midnight), pytz.timezone('UTC'), is_dst=False)
        ed = (sd + timedelta(days=1))
        test_url = '/api/reporting/products/sales?startdate={sd}&enddate={ed}&interval=day'.format(
                sd=sd.strftime(urldf),
                ed=ed.strftime(urldf))
        response = self.client.get(test_url)
        oi = OrderItems.objects.filter(order__orderDate__range=[sd,ed]).values('product_id')\
                .annotate(quantity_sold=Sum('quantity'), product_sales_revenue=Sum('price'))
        body = json.loads(response.content)
        for r in body['results']:
            print(r)
            qs = oi.filter(product_id=r['product_id']).values('quantity_sold')
            ps = oi.filter(product_id=r['product_id']).values('product_sales_revenue')
            print(qs, ps)
            self.assertEquals(int(r['quantity_sold']), qs[0]['quantity_sold'])
            self.assertEquals(float(r['product_sales_revenue']), float(ps[0]['product_sales_revenue']))
    
    def test_api_returns_product_sales_by_period_month(self):
        """Tests that the api returns product sales by in a particular month"""
        urldf = '%m-%d-%Y'
        dateToCheck = datetime.strptime('11-01-2016', urldf) #Orders.objects.all().values('orderDate')[0]['orderDate']
        dateToCheck = timezone.make_aware(dateToCheck, pytz.timezone('UTC'), is_dst=False)
        sd = dateToCheck
        ed = (dateToCheck + timedelta(days=30))
        print(sd, ed)
        test_url = '/api/reporting/products/sales?startdate={sd}&enddate={ed}&interval=month'.format(
                sd=sd.strftime(urldf),
                ed=ed.strftime(urldf))
        response = self.client.get(test_url)
        oi = OrderItems.objects.filter(order__orderDate__range=[sd,ed]).values('product_id')\
                .annotate(quantity_sold=Sum('quantity'), product_sales_revenue=Sum('price'))
        body = json.loads(response.content)
        for r in body['results']:
            qs = oi.filter(product_id=r['product_id']).values('quantity_sold')
            ps = oi.filter(product_id=r['product_id']).values('product_sales_revenue')
            self.assertEquals(int(r['quantity_sold']), qs[0]['quantity_sold'])
            self.assertEquals(float(r['product_sales_revenue']), float(ps[0]['product_sales_revenue']))
