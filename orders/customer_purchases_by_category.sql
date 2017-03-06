-- Answer to question 3 --
SELECT customerId as 'customer_id', first_name as 'customer_first_name', categoryId as 'category_id', c.name as 'category_name', sum(oi.quantity) as 'number_purchased'
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

