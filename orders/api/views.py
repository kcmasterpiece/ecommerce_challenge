from api.models import *
import simplejson as json
from datetime import datetime
from django.db import connection
from django.core import serializers
from django.http import JsonResponse
from api.queryHelper import QueryHelper

# Create your views here.
def displayCustomerOrders(request, customer_id):
    """I hate this method and how it construct the JSON.  I am sure there is a better
    way to do this in Django but I haven't figured it out yet"""
    if customer_id:
        # check if customer has orders
        orders = Orders.objects.filter(customer_id=customer_id)
        if orders.exists():
            c = Customers.objects.get(customerId=customer_id)
            data = { 'customer': {
                                     'customerId': c.customerId,
                                     'first_name': c.first_name,
                                     'last_name': c.last_name                               
                                 },
                     'orders': [{
                                    'orderId': o.orderId,
                                    'orderStatus': o.get_orderStatus_display(),
                                    'orderDate': str(o.orderDate),
                                    'orderTotal': o.orderTotal,
                                    } for o in orders]
                    }
            for i in range(0,len(data['orders'])):
                data['orders'][i]['orderItems'] = [{
                    'orderItemId': oi.orderItemId,
                    'productId': oi.product_id,
                    'productName': oi.productName,
                    'quantity': oi.quantity,
                    'price' : oi.price
                } for oi in OrderItems.objects.filter(order_id=data['orders'][i]['orderId'])]
            # data = json.dumps(data)
            return JsonResponse(data, safe=False)

        else: 
            return JsonResponse({'message':'no orders found for customer'})
    else:
        return JsonResponse({'message':'customer info not found'})
    
def productSalesByPeriod(request):
    """ Performing this query is very complicated in Django's ORM, so using SQL"""
    dateFormat = '%m-%d-%Y'
    sqlDateFromat = '%Y-%m-%d'
    startdate = datetime.strptime(request.GET.get('startdate'), dateFormat)
    enddate = datetime.strptime(request.GET.get('enddate'), dateFormat)
    interval = request.GET.get('interval') 
    possibleIntervals = ['day', 'week', 'month']
    if interval not in possibleIntervals:
        return JsonResponse({'message': 'interval not found'})
    cursor = connection.cursor()
    # This should be a stored procedure in production to prevent SQL injection
    query = '''
        SELECT product_id, productName, intervalNumber as '{interval}_number', 
            sum(price) as 'product_sales_revenue', sum(quantity) as 'quantity_sold'
        FROM (
                SELECT product_id, productName, 
                    CASE 
                        WHEN '{interval}' != 'day' THEN 
                            CONVERT(
                                CONCAT(YEAR(o.orderDate), 
                                    IF({interval}(o.orderDate)<10, CONCAT(0, {interval}(o.orderDate)), {interval}(o.orderDate))), UNSIGNED INTEGER
                                )
                        ELSE 
                            CONVERT(
                                CONCAT(YEAR(o.orderDate),
                                        MONTH(o.orderDate),
                                        IF(day(o.orderDate)<10, CONCAT(0, day(o.orderDate)), day(o.orderDate))),
                                    UNSIGNED INTEGER)
                        
                    END as intervalNumber,
                    price, quantity
                FROM api_orderitems oi
                INNER JOIN api_orders o
                        on o.orderId = oi.order_id
                WHERE o.orderDate >= '{startdate}' and o.orderDate <= '{enddate}'
        ) as items
        GROUP BY
            product_id, productName, intervalNumber
        ORDER BY 
            intervalNumber, product_id
        '''.format(interval=interval, startdate=startdate.strftime(sqlDateFromat), 
                enddate=enddate.strftime(sqlDateFromat))
    cursor.execute(query)
    results = QueryHelper.dictfetchall(cursor)
    results
    response = {'parameters' : { 'interval' : interval,
                            'startdate' : startdate,
                            'enddate' : enddate
                            },
                'results': results
                }
    return JsonResponse(response, safe=False)
