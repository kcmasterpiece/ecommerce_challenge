# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-03 23:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('categoryId', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('orderItemId', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('productName', models.CharField(default=None, max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('orderId', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('orderDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('orderTotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Customers')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategories',
            fields=[
                ('productCategoryId', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Customers')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Products')),
            ],
        ),
        migrations.AddField(
            model_name='orderitems',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Orders'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Products'),
        ),
    ]
