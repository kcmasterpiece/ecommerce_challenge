SELECT customerId, first_name, categoryId, c.name, sum(oi.quantity) 
FROM api_customers cus
INNER JOIN api_orders o
	on o.customer_id = cus.customerId
INNER JOIN api_orderItems oi
	on oi.order_id = o.orderId
INNER JOIN api_products p 
	on p.productId = oi.product_id
INNER JOIN api_productcategories pc
	on p.productId = pc.product_id
INNER JOIN api_categories c
	on pc.category_id = c.categoryId
GROUP BY customerId, first_name, categoryId, c.name;

-- on one line for easy use in terminal--
SELECT customerId as 'order__customer_id', first_name as 'order__customer__first_name', categoryId as 'product__productcategories__category__categoryId', c.name as 'product__productcategories__category__name', sum(oi.quantity) as 'number_purchased'  FROM api_customers cus INNER JOIN api_orders o  on o.customer_id = cus.customerId INNER JOIN api_orderItems oi  on oi.order_id = o.orderId INNER JOIN api_products p   on p.productId = oi.product_id INNER JOIN api_productcategories pc  on p.productId = pc.product_id INNER JOIN api_categories c  on pc.category_id = c.categoryId GROUP BY customerId, first_name, categoryId, c.name; 
