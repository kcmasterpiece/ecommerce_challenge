# Ecommerce Coding Challenge

Here is a coding challenge I recently completed using Python/django/mysql. I used some SQL where django's ORM proved difficult to wrangle for the desired output. I produced a very bare bones ecommerce app with the following features:

- Backend/data models:
	- Customers can place orders for many products
	- Products and categories have a many-to-many relationship
	- Orders can have a status

- Reporting:
	- Endpoint url `api/customers/orders/[customerId]` returns all orders for a customer
	- Endpoint url `api/reporting/products/sales?startdate=[startdate]&enddate=[enddate]&interval=[interval]` produces a report of product sales over a given period (date format MM-DD-YYYY) by a specified interval (options: day, week, month)
	- Both return JSON

 - Tests:
	- Unit tests test that urls produce the desired results, that the data model works as expected, and that logic works as expected
	- I wrote some scripts that generate about a dozen randomized orders for about half a dozen customers so that I could validate reporting outputs without having to hard code a bunch of data.

It was a fun challenge. Needless to say, there are many things I would improve if I kept working this, including:
- better urls/views structure within the project
- unittests that only use assert once
- security
- exception handling and checking that values provided by a user are valid and not malicious
- possibly using stored procedures and making sure that values sent directly into sql syntax are not sql injection attempts

