from django.test import TestCase
from django.db import connection
from api.models import Customers, Products, Categories, Orders, OrderItems, ProductCategories
from api.businessLogic import OrderMethods
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

        # Test order matches
        saved_orders = Orders.objects.all()
        order = OrderMethods.createOrder(items, customer=customer)
        
        # Check customer matches
        self.assertEqual(saved_orders[0].customer, order.customer)
        
        # Check order total matches
        self.assertEqual(saved_orders[0].orderTotal, order.orderTotal)

        # Check order products match (items won't match as id's will be different)
        orderProducts = lambda orderItems: [oi.product for oi in orderItems]
        self.assertEqual(set(orderProducts(OrderItems.objects.filter(order=order))),
                         set(orderProducts(OrderItems.objects.filter(order=saved_orders[0])))
                         )

    def test_all_statuses_are_available(self):
        """Tests that all order statuses are available for use"""
        statuses = set(['waiting for delivery','on its way', 'delivered'])
        orderStatuses = set([d for (v, d) in Orders._meta.get_field('orderStatus').choices])
        self.assertEquals(statuses, orderStatuses)

    def test_orders_can_have_status(self):
        """Tests that orders can have status"""
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

    def test_order_method_number_purchased_by_customer_by_category(self):
        generate_data.main()
        
        def dictfetchall(cursor):
            "Return all rows from a cursor as a dict"
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
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
        results = dictfetchall(cursor)
        ormResults = OrderMethods.number_purchased_by_customer_and_category()
        # since raw query returns value as 'Decimal('n')', convert values
        for i in range(0,len(results)):
            results[i]['number_purchased'] = int(results[i]['number_purchased'])
        
        for row in ormResults:
            self.assertIn(row, results)    

