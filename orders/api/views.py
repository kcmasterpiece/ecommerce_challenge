from api.models import *
import simplejson as json
from django.core import serializers
from django.http import JsonResponse

# Create your views here.
def displayCustomerOrders(request, customer_id):
    """I hate this method and how it construct the JSON.  I am sure there is a better
    way to do this in Django but I don't know it and haven't figured it out yet"""
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
        return JsonResponse("{'message':'customer info not found'")
