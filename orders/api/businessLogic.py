from api.models import *
from django.db.models import Sum

class OrderMethods:
    @staticmethod
    def createOrder(products, customer=None, first_name=None, last_name=None):
        """Creates an order given the supplied info:

        :customer: the customer object for this customer, if not supplied a new customer record will be created
        :first_name: customer's first name, used if no customer record is provided
        :last_name: customer's last name, used if no customer record is provided
        :products: products to be purchased for this order
        :returns: an order object

        """
        if customer == None:
            customer = Customers.objects.create(first_name=first_name,last_name=last_name)
        orderTotal = sum(float(p.price) for p in products)
        order = Orders.objects.create(orderTotal = orderTotal, customer=customer)
        for p in products:
            orderItem = OrderItems.objects.create(product=p, productName=p.name, price=p.price, quantity=1, order=order)
        return order

    @staticmethod
    def number_purchased_by_customer_and_category():
        """Returns the same results as the SQL query in question 3"""
        return OrderItems.objects.values(
                'order__customer_id',
                'order__customer__first_name',
                'product__productcategories__category__categoryId',
                'product__productcategories__category__name')\
                    .annotate(number_purchased=Sum('quantity'))

