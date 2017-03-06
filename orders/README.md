# Shipt Coding Challenge Answers

## Produced by Jeff Fontas

I used Python/django to produce this solution.  I assume you know how to run this if you have any inclination of doing so.  I used MySQL, so a mysql db called 'DB' with user root and '' as password must exist in order to run tests and view this as a working solution.  I have included requirements.txt for virtualenv.  This was built using python3. The contents of the .zip file provided is a git repository.

Needless to say, there are many things I would improve if I was working on production code, including:
	- adding a SKU field to the products table.  It wasn't necessary for this exercise but it would be in product (plus many other product meta fields)
	- better urls/views structure within the project
	- unittests that only use assert once
	- security
	- exception handling and checking that values provided by a user are valid and not malicious
	- possibly using stored procedures and making sure that values sent directly into sql syntax are not sql injection attempts

These are just off the top of my head, I have not used django in production so I may not have used customs/best practices for everything written here.

The data model speaks for itself, I could explain it further but I will let it stand on its own. I do explain some design choices in the random notes/assumptions below.

Other random notes/assumptions:

1. I assume that all responses from the api endpoints will return Json.  I also assume the structure of this JSON is arbitrary and that I am free to define my own structure
2. I have not used error status codes when returning failure messages at these endpoints, though I would in production
3. Why is productName stored in the orders table if it is stored in the products table? Product prices and names could change in the products table.  When an order is placed the orderItems table should record the price and name at the time the order was placed
4. There are limited fields in making up an order.  Obviously we would need taxes, discounts, etc in a production db.

## Conceptual Questions

### 1. We want to give customers the ability to create lists of products for one-click ordering of bulk items. How would you design the tables, what are the pros and cons of your approach?

I would create a separate tables called "one_click_orders" and "one_click_order_items".  Columns would have the following columns:

one_click_orders:
one_click_order_id (PK)
customer_id (FK)

one_click_order_items:
one_click_order_item_id (PK)
one_click_order_id (FK)
product_id (FK)
quantity

The tables would just contain a list of the products the customer would like to buy in a one-click purchase.  Obviously, rules would need to be created to handle various situations that will eventually arise:
	- there will be a time when a product is not available for purpose (no inventory)
	- there will be a time when not enough inventory is available at the desired quantity
	etc.

When the time comes, the regular order methods used to create orders would surely be able to take the list of products supplied in the list the customer is interested in purchasing as a parameter and place the order.

As standard practice, I usually include date_created and date_modified, as long as created_by and modified_by records on all tables, unless it is truly not necessary.  While they aren't included above, they'd probably be a good idea here. 

Pros:
This structure allows customers to create multiple one-click order lists, if this is necessary.

Cons:
This structure is very normalized.  This same data set could be stored in a list/array of customers in a column on the customer record, if only one list is possible per customer.  This would eliminate the need to create any tables, although queries would be a tremendous pain (requiring splitting/manipulating the column data).  One list per customer could also be accomplished with one table that just maintains a record of the customer_id and product_id for each product the customer is interested in.  
At least one join would be required to get this data.


### 2. If Shipt knew exact inventory of stores, and when facing a high traffic and limited supply of particular item, how do you distribute the inventory among customers checking out?

This question raises a lot more:
	- Is a customer guaranteed an item if they place an order? i.e. if there is one left at the store and they buy, do they automatically get it or does the shopper have to get to their hands on it for the customers to actually get it?
		I assume no since many inventory issues could arise regularly that would prohibit this
	- How do we handle payment? Does it happen before or after an order is picked up? (When a customer pays, we will need to know what inventory they are definitely going to get)
		I assume when the order is delivered.  I also assume they will only pay for what the shopper marks they have bought
	- Do customers shop for items at a specific store, or do they shop for items generally, and Shipt chooses the store closest to them that can fulfill the order?
		I can envision multiple options, but I am going to keep it simple here and assume that all inventory is purchased from one store.


In high traffic situations within the Shipt ordering system, inventory could be "distributed" or bought in a few ways.  One way is to just let the system evaluate which inventory is available when the "place order" button is pushed, and alert the customer if something is unavailable while placing an order for the rest. Of course, if items are out of stock while the customer is creating an order they would not be allowed to add them to their basket.  In this way, inventory could be distributed on a first-come, first-served basis, provided that if a shopper is handling multiple orders they honor timestamps on the orders when determining who gets the last banana.  I am assuming there is some mechanism that finalizes the order and charges the customer, so that if the store is actually out, the inventory provided to Shipt is not accurate, or some other issue arises, the customer will ultimately only be billed for what they buy.

Another way that the ordering system could distribute inventory is to let customers 'reserve' inventory when they add it to their basket.  I'd have to think a little bit more about when it is most appropriate for the time clock to click in, but for this example let's just say it is once the item is added to the basket.  And hypothetically, let's say the time limit on the reservation is 10 minutes.  On the backend, when an basket item record is created in the database, it will have a "date_created" field.  If any other customer tries to purchase this product, the system will look at the product's inventory level, minus the inventory level for all the basket items created < 10 mins ago.  The customer would only be able to purchase the inventory level that remains after this calculation is performed.   The unfortunate part of this strategy is that inventory could potentially NOT be purchased since people add items to their basket all the time but never purchase.  So the moment at which the reservation clock kicks in, and the time limit, will have to be really dialed in to match the moment at which people are incredibly likely to buy, and the reservation time equals the average time to buy + a standard deviation or so.  I also like this solution because it may help in preventing race conditions when two orders are placed for the same item at nearly the same time.  

There could also be instances where it makes sense to "swap" the destinations of orders to better match inventory to customers.  For example, if all customer 1's products are available at store A and store B, but customer 2's products are only available at store B, and customer 1 placed an order that got directed to store B, and took all the inventory for an item in customer 2's order.  In such a scenario, if both orders were placed at almost the same time, and both orders could be fulfilled if we fulfilled customer 1's order from store A instead of store B, we can optimize the process so that everyone gets most of what they want.  Obviously, this could get very complex very quickly, but there may be opportunities here to take advantage of knowing what people want and where inventory is so that the most inventory can be sold.
