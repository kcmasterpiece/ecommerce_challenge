# This file generates data in the production db so that the queries can be executed
import random
import datetime
from django.utils import timezone
import pytz
from api.models import *
from api.businessLogic import OrderMethods
from randomDate import randomDate

def main():

    # Create some customers
    customers = [ Customers.objects.create(first_name='Philip', last_name='Wheeler'),
            Customers.objects.create(first_name='Amanda', last_name='Willis'),
            Customers.objects.create(first_name='Daniel', last_name='Little'),
            Customers.objects.create(first_name='Melissa', last_name='Myers'),
            Customers.objects.create(first_name='Peter', last_name='Dean'),
            Customers.objects.create(first_name='Janet', last_name='Stanley')]
    customers = customers + customers + customers + customers
    # Create some products
    products = [Products.objects.create(name='13 inch MacBook Pro', price='1799.00'),
             Products.objects.create(name='15 inch MacBook Pro', price='1999.00'),
             Products.objects.create(name='17 inch MacBook Pro', price='2199.00'),
             Products.objects.create(name='Mighty Mouse', price='99.00'),
             Products.objects.create(name='Keyboard', price='89.00'),
             Products.objects.create(name='30 inch Monitor', price='489.00')]
             
    # Create some categories
    categories = [Categories.objects.create(name='Computers'),
                  Categories.objects.create(name='Accessories'),
                  Categories.objects.create(name='Monitors'),
                  Categories.objects.create(name='Laptops')]

    # Add products to categories
    productCategories = []
    for p in products:
        for c in categories:
            if 'MacBook Pro' in p.name and c.name in ['Computers','Laptops']:
                ProductCategories.objects.create(category=c, product=p)
            if 'Monitor' in p.name and c.name in ['Monitors','Accessories']:
                ProductCategories.objects.create(category=c, product=p)
            if float(p.price) < 100 and c.name == 'Accessories':
                ProductCategories.objects.create(category=c, product=p)

    # Create some orders
    for c in customers:
        orderItems = []
        for i in range(1,random.randint(1,len(products))):
            orderItems.append(random.choice(products))
        order = OrderMethods.createOrder(orderItems, customer=c)
        dateFormat = '%Y-%m-%d %H:%M:%S'
        enddate = datetime.datetime.now().__format__('%Y-%m-%d %H:%M:%S')
        od = randomDate('2016-11-01 00:00:00', enddate, random.random())
        order.orderDate = timezone.make_aware(datetime.datetime.strptime(od, dateFormat), pytz.timezone('America/Los_Angeles'), is_dst=False)
        order.save()

