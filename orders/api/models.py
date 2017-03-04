from django.db import models
from django.utils import timezone

# Create your models here.
class Customers(models.Model):
    customerId = models.AutoField(primary_key=True, db_index=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)

class Products(models.Model):
    productId = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)

class Categories(models.Model):
    categoryId = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=100)

class ProductCategories(models.Model):
    productCategoryId = models.AutoField(primary_key=True, db_index=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)


class Orders(models.Model):
    orderId = models.AutoField(primary_key=True, db_index=True)
    customer = models.ForeignKey(Customers)
    orderDate = models.DateTimeField(default=timezone.now)
    orderTotal = models.DecimalField(decimal_places=2, max_digits=10)
    statuses = [( 1 , 'waiting for delivery'),
                ( 2 , 'on its way'),
                ( 3 , 'delivered')]
    orderStatus = models.IntegerField(choices=statuses, default=1)

class OrderItems(models.Model):
    orderItemId = models.AutoField(primary_key=True, db_index=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(Products)
    productName = models.CharField(max_length=100, default=product.name)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField()
