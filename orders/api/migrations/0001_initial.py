# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-03 22:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customers',
            fields=[
                ('customerId', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
