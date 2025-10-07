from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F
from django.db import transaction, connection
from django.db.models import Count, Min, Max, Avg, Sum, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from store.models import Product, Customer, Collection, Order, OrderItem
from tags.models import TaggedItem


def say_hello(request):
# The following line uses Django's ORM (Object-Relational Mapper) to fetch data from the database.
# 
# Product.objects.all() does NOT immediately fetch all products from the database.
# Instead, it creates a QuerySet, which is a lazy object representing the query.
# 
# - "Product" is the model class representing a table in the database.
# - ".objects" is the model manager that provides access to ORM query methods.
# - ".all()" creates a QuerySet for all rows in the "Product" table.
#
# Under the hood:
# - Django builds a SQL query (like "SELECT * FROM store_product") but does NOT run it yet.
# - The actual database query happens only when you iterate over the QuerySet (e.g., in a for loop),
#   convert it to a list, or otherwise force evaluation.
# - This lazy evaluation makes queries efficient, as you can further filter or slice the QuerySet before hitting the database.
#
# Example:
#   query_set = Product.objects.all()  # No database access yet!
#   for product in query_set:          # Database query runs here, fetching products one by one.

    query_set = Product.objects.all()
    query_set = query_set.filter(title='Bread Ww Cluster').order_by('-unit_price')  # Further filtering the QuerySet (still no DB access)

    # Here in query_set = list(query_set)  Executed SQL

# SELECT "store_product"."id",
#        "store_product"."title",
#        "store_product"."slug",
#        "store_product"."description",
#        "store_product"."unit_price",
#        "store_product"."inventory",
#        "store_product"."last_update",
#        "store_product"."collection_id"
#   FROM "store_product"
#  WHERE "store_product"."title" = 'Bread Ww Cluster'
#  ORDER BY "store_product"."unit_price" DESC
    
    for product in query_set:
        print(product)


# Retrieving a single object by primary key (id)
    # if you try to get a product that does not exist, it will raise an exception
    try:
        # Fetches a single product with primary key 1 (executes SQL immediately). pk is shorthand for primary key. in django pk automatically maps to id field
        product = Product.objects.get(pk=1) 
        # Both are same. id and pk are interchangeable in this context. id is the actual field name in the model, while pk is a more general term that always refers to the primary key of the model.
        product = Product.objects.get(id=1)
    
    except ObjectDoesNotExist:
        pass
    
    exist_bool = Product.objects.filter(id=1).exists()  # Returns True if a product with id=1 exists, otherwise False
    product_2 = Product.objects.filter(id=0).first()  # Returns None if no match is found, avoiding exception


    # Filtering objects with LooksUp. field lookups examples: exact, iexact, contains, icontains, in, gt, gte, lt, lte, startswith, istartswith, endswith, iendswith, range, date, year, month, day, week_day, isnull, search, regex, iregex are available to use.
    # Field lookups are used to create more complex queries by specifying conditions on model fields.
    # queryset_filter = Product.objects.filter(unit_price__gt =20)
    queryset_filter = Product.objects.filter(unit_price__range =(20,30))
    # we can use multiple filters like startswith and endswith, etc.
    queryset_filter2 = Product.objects.filter(title__contains='coffee')  # Case-sensitive contains
    queryset_filter3 = Product.objects.filter(title__icontains='coffee')  # Case-insensitive contains
    queryset_filter4 = Product.objects.filter(title__istartswith='coffee')  # Case-insensitive startswith
    queryset_filter5 = Product.objects.filter(last_update__year='2021')  # Products updated in the year 2023
    queryset_filter6 = Product.objects.filter(description__isnull=True)  # Products with no description


    queryset_filter7 = Customer.objects.filter(email__endswith='.com')  # Customers with email ending in .com
    queryset_filter8 = Product.objects.filter(inventory__lt=10)  # Products with inventory less than 10
    queryset_filter9 = Order.objects.filter(pk=1) # Orders with primary key 1

    # Complex lookups using Q objects for OR conditions
    # inventory < 10 AND unit_price < 20
    queryset_filter10 = Product.objects.filter(inventory__lt=10, unit_price__lt=20)  # AND condition
    queryset_filter11 = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)  # Chained filters (also AND condition). filter returns a query set. when call by list(name) then queryset evaluated.
    
    # inventory < 10 OR unit_price < 20
    queryset_filter12 = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))  # OR condition using Q objects
    queryset_filter13 = Product.objects.filter(Q(inventory__lt=10) & Q(unit_price__lt=20))  # AND condition using Q objects
    queryset_filter14 = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))  # inventory < 10 AND NOT (unit_price < 20) using Q objects

    # Referencing related fields using F objects
    # Products: inventory = unit_price
    # queryset_filter15 = Product.objects.filter(inventory=unit_price) # This will raise an error because unit_price is not defined in this scope. To reference model fields, we should use F objects from django.db.models.
    # queryset_filter16 = Product.objects.filter(inventory=F('unit_price'))  # Using F objects to reference model fields


# F Object
# Purpose: Reference model field values directly in queries and updates.
# Use Case: When you want to compare a field to another field, or perform arithmetic using field values.
# Example: Find products where inventory equals unit_price:

# Q Object
# Purpose: Build complex queries with AND, OR, and NOT logic.
# Use Case: When you need to combine multiple conditions, especially with OR or NOT.
# Example: Find products where inventory < 10 OR unit_price < 20:

    # Sorting
    queryset_filter17 = Product.objects.order_by('title') # Ascending order by title
    queryset_filter18 = Product.objects.order_by('title', '-unit_price') # Ascending by title, then descending by unit_price
    queryset_filter19 = Product.objects.order_by('title', '-unit_price').reverse() # Reverse the order of the previous sorting
    
    queryset_filter20 = Product.objects.order_by('unit_price')[0] 
    queryset_filter21 = Product.objects.earliest('unit_price') # returns the object with the lowest unit_price


    # Limiting results
    queryset_filter22 = Product.objects.all()[:5]  # First 5 products
    queryset_filter23 = Product.objects.all()[5:10]


    # Selecting fields for query (to optimize performance)
    # by default, Django retrieves all fields of a model when you query it.
    # However, if you only need specific fields, you can use .only() or .values() to limit the fields fetched from the database.

    queryset_filter24 = Product.objects.values('id', 'title')  # Returns dictionaries with only 'id' and 'title' fields
    queryset_filter25 = Product.objects.values('id', 'title', 'collection__title')  # Including related field 'collection.title'. it will return type of dictionary
    queryset_filter26 = Product.objects.values_list('id', 'title', 'collection__title')  # Returns tuples with 'id', 'title', and 'collection_id' fields

    # Select Product that have been ordered and sort by title
    queryset = OrderItem.objects.values('product_id').distinct() # you can call product_id or product__id both are same. but product_id is faster because it does not involve a join. and distinct() is used to eliminate duplicate product ids.
    queryset2 = Product.objects.filter(id__in=queryset).order_by('title') # Select Products that have been ordered and sort by title. here id__in is used to filter products whose id is in the list of product ids from the OrderItem queryset.
    
    # values() vs only()
    # .values() returns dictionaries with only the specified fields, while .only() returns model
    queryset3 = Product.objects.only('id', 'title')  # Fetches only 'id' and 'title' fields, other fields are deferred until accessed
    ## Warning: Using .only() can lead to additional database queries if you access deferred fields later, so use it judiciously. only use it when you are sure you won't need the other fields.
    ## IF you dont know what you are doing, you end up with N+1 query problem. so be careful when using only().

    queryset4 = Product.objects.defer('description')  # Fetches all fields except 'description', which is deferred until accessed
    ## Warning: Similar to .only(), using .defer() can lead to additional queries if deferred fields are accessed later. so use it judiciously.
    ## if you use for loop and inside the loop you access the deferred field, it will make a query for each iteration. so be careful when using defer().
    

    ## Selecting related objects to avoid N+1 query problem
    queryset5 = Product.objects.all()  # This will cause N+1 query problem if you access related fields in a loop. here this will call only all products query. but when you access related fields like collection.title in a loop, it will make a query for each product to fetch the related collection.
    queryset6 = Product.objects.select_related('collection').all()  # This will fetch related collection in the same query using a SQL join. use select_related for ForeignKey and OneToOne relationships only. it is faster because it uses a SQL join and preloads the related objects in a single query.
    # use select_related when you know you will need the related object and you want to avoid additional queries.
    # and select_related (1) is used for single-valued relationships (ForeignKey, OneToOneField). 
    # if you have multi-valued relationships (ManyToManyField, reverse ForeignKey), use prefetch_related instead.

    queryset7 = Product.objects.prefetch_related('promotions').all()  # This will fetch related promotions in a separate query and join them in Python. use prefetch_related for ManyToMany and reverse ForeignKey relationships. it is useful when you have a lot of related objects and you want to avoid loading them all at once.
    # use prefetch_related when you have multi-valued relationships and you want to avoid loading

    # Get the last 5 orders with their customer and items (include product)
    queryset8 = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5] # here orderitem_set is the reverse relationship from OrderItem to Order. django automatically creates a reverse relationship for ForeignKey fields. and you can access it using the model name in lowercase followed by _set. you can change the name of the reverse relationship by adding related_name parameter in ForeignKey field. here we are using double underscore to access the product field of the OrderItem model. this will prefetch all the products related to the order items in a separate query and join them in python. this will avoid N+1 query problem when you access orderitem_set and product fields in a loop.

    # Aggregating objects.
    # from django.db.models import Count, Min, Max, Avg, Sum
    result = Product.objects.aggregate(Count('id')) # Total number of products. it will return a dictionary with the key as id__count and value as the count of products not the queryset.
    result2 = Product.objects.aggregate(count=Count('id')) # Total number of products with custom key name. it will return a dictionary with the key as count and value as the count of products.
    result3 = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price')) # Total number of products and minimum unit price. it will return a dictionary with the keys as count and min_price and values as the count of products and minimum unit price respectively.

    # Annotating objects. (similar to aggregate but it returns a queryset with the aggregated values for each object in the queryset)
    # we need to pass an expression to annotate() method. expression can be an aggregate function or a F object or a combination of both.
    # example of all expressions: Count, Sum, Avg, Max, Min, F, Value, Case, When, Q, etc.
    result4 = Customer.objects.annotate(is_new=Value(True)) # Annotate each customer with a new field 'is_new' set to True. here Value(True) is used to create a constant value for the new field.
    result5 = Customer.objects.annotate(new_id=F('id')+1) # Annotate each customer with a new field 'new_id' which is id + 1. here F('id') is used to reference the id field of the Customer model.

    # Calling Database Functions
    result6 = Customer.objects.annotate(full_name=Func(F('first_name'),Value(' '), F('last_name'), function='CONCAT')) # Annotate each customer with a new field 'full_name' which is the concatenation of first_name and last_name. here Func is used to call a database function. CONCAT is a SQL function that concatenates two or more strings. this will work only if your database supports CONCAT function. if you are using sqlite, you can use || operator instead of CONCAT function.
    # alternatively, you can use Concat function from django.db.models.functions
    result7 = Customer.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name')) # This is a more portable way to concatenate strings across different databases. it will work with all databases supported by django.
    # Func vs Concat
    # Func is a generic way to call any database function. you need to specify the function name as a string. it may not be portable across different databases if the function name or syntax is different.
    # Concat is a specific function provided by django to concatenate strings. it is portable across different databases and handles the syntax differences internally. it is recommended to use Concat for string concatenation

    # Grouping data: 
    result8 = Customer.objects.annotate(order_count=Count('order')) # Annotate each customer with the number of orders they have placed. here order is the reverse relationship from Order to Customer. django automatically creates a reverse relationship for ForeignKey fields. and you can access it using the model name in lowercase followed by _set. you can change the name of the reverse relationship by adding related_name parameter in ForeignKey field. here we are counting the number of orders for each customer and annotating it as order_count. but here insted of order_set we use order because django automatically removes the _set suffix when using aggregate functions. if we use order_set it will raise an error because order_set is not recognized as a valid field for aggregation.
    
    # working with expressions wrappers
    # sometimes you need to perform operations that are not directly supported by the database functions or F objects.
    # in such cases, you can create custom expressions by subclassing Func or using Expression
    result9 = Product.objects.annotate(discounted_price=F('unit_price') * 0.8) # this will raise an error because you cannot multiply a F object directly with a float. you need to use ExpressionWrapper to wrap the expression and specify the output field type.
    result9 = Product.objects.annotate(discounted_price=ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())) # Annotate each product with a new field 'discounted_price' which is 80% of the unit_price. here ExpressionWrapper is used to wrap the expression and specify the output field type as DecimalField. this is necessary because the result of the expression is not automatically inferred by django. you need to tell django what type of field to expect as the result of the expression.

    # Quering generic relationships
    # Generic relationships allow a model to reference any other model in the database.
    # This is useful when you want to create a relationship that can point to multiple models.
    # To create a generic relationship, you need to use GenericForeignKey from django.contrib.contenttypes.
    content_type = ContentType.objects.get_for_model(Product) # Get the ContentType for the Product model. ContentType is a model that stores information about all the models in the database.
    result10 = TaggedItem.objects\
            .select_related('tag')\
            .filter(content_type=content_type, 
                    object_id=1
            ) # Get all tags for the product with id 1. here content_type is the ContentType for the Product model and object_id is the id of the product. this will return all TaggedItem objects that are related to the product with id 1. we use select_related to fetch the related tag in the same query to avoid N+1 query problem.
    # Alternatively.
    product = TaggedItem.objects.get_tags_for(Product, 1) # Get all tags for the product with id 1 using the custom manager method. here we are using a custom manager method get_tags_for to get all tags for a given model and object id. this method is defined in the TaggedItem model's manager. this is a more convenient way to get tags for a product without having to deal with ContentType and object_id directly.

    # QuerySet caching
    # QuerySets are lazy and are not evaluated until you iterate over them, convert them to a list, or access their data in some other way. 
    # Once a QuerySet is evaluated, it is cached and subsequent accesses to the same QuerySet will use the cached data instead of hitting the database again.
    # This caching behavior can improve performance by reducing the number of database queries, but it also means that if the underlying data changes, the QuerySet will not reflect those changes unless it is re-evaluated.
    product = Product.objects.all()  # QuerySet is created, no database access yet.
    product = list(product)  # QuerySet is evaluated, database query is executed
    product = list(product)  # Uses cached data, no additional database query
    # reading data from the database/disk is slow. so if you are going to use the same queryset multiple times, it is better to cache it in a variable and use it instead of calling the database multiple times. because reading from memory is much faster than reading from the database/disk.
    product2 = product[0]  # Accessing the first product from the cached list, no database query.
    # Warning: If you modify the database (e.g., add, update, delete records) after a QuerySet has been evaluated, the cached data will not reflect those changes. You would need to create a new QuerySet to see the updated data.
    # Warning: Caching happens only if it evaluated the entire QuerySet first. if you slice the QuerySet before evaluating it, only the sliced portion is cached. for example, if you do product = Product.objects.all()[:5] and then evaluate it, only the first 5 products are cached. if you access product[5], it will hit the database again to fetch the 6th product.


    # Creating Objects/inserting into the database.
    collection = Collection() # Create a new Collection instance (not saved to the database yet)
    # we can set the fields using keyword arguments in the constructor like Collection(title='New Collection') or we can set the fields directly like below.
    # but setting with keyword arguments you dont get automplete and type checking in some IDEs. and in refactoring, if you change the field name in the model, it will not be reflected in the keyword arguments. so it is better to set the fields directly.
    collection.title = 'Video Games 2' # Set the title field
    collection.featured_product = Product(pk=1) # assuming a product with pk=1 already exists
    #collection.featured_product_id = 1 # Alternatively, you can set the foreign key directly using the _id suffix.
    # here _ and __ are different. _ is used to access the field directly, while __ is used to access related fields in lookups. 
    collection.save() # Save the Collection to the database (INSERT operation)

    # Alternatively, you can create and save an object in one step using the create() method of the model manager.
    Collection.objects.create(title='Books', featured_product=Product(pk=2)) # Create and save a new Collection in one step (INSERT operation). here we are assuming a product with pk=1 already exists. if it does not exist, it will raise an IntegrityError because of the foreign key constraint. it automatically calls save() method internally.




    # Updating Objects.
    # To update an object, you first retrieve it from the database, modify its fields, and then call save() to persist the changes.
    collection = Collection(pk=11) # Retrieve the Collection with primary key 11 (does not hit the database yet)
    collection.title = 'Video Games edited'
    collection.featured_product = None
    collection.save() # Save the changes to the database (UPDATE operation) because the object already has a primary key. update and create only differ in the presence of primary key.

    # If you want to update singele field like below.
    collection = Collection(pk=11)
    collection.featured_product = None
    collection.save()
    # Warning: someting crazy happens. it will set rest of the fields to their default values or null if they are nullable. so be careful when updating single fields using this method. because it will overwrite the other fields with default or null values.

    # to update Properly, first fetch the object from the database. this way you get all the fields with their current values.
    collection = Collection.objects.get(pk=18) # Fetch the Collection from the database (hits the database). you might thing it is inefficient because it hits the database twice (once for get and once for save). but it is better to be safe than sorry. because you dont want to accidentally overwrite other fields with default or null values. and most cases, it will not be a performance issue unless you are doing it in a loop or bulk operation.
    collection.featured_product = None
    collection.save() # Save the changes to the database (UPDATE operation)

    # If you want to update multiple fields or multiple objects at once, you can use the update() method of the model manager. this method hits the database only once and does not call the save() method of the model, so it does not trigger any signals or validations.
    Collection.objects.update(featured_product=None) # Set featured_product to None for all collections (UPDATE operation). this will hit the database only once and set featured_product to None for all rows in the collection table.

    # to update a subset of objects, you can filter them first and then call update().
    Collection.objects.filter(pk=24).update(featured_product=12) # Set featured_product to 11 for the collection with primary key 11 (UPDATE operation). this will hit the database only once and set featured_product to None for the row with pk=11 in the collection table.



    # Deleting Objects.
    # we can delete a single object or multiple objects at once.
    collection = Collection(pk=11) # Create a Collection instance with primary key 11 (does not hit the database yet)
    collection.delete() # Delete the Collection from the database (DELETE operation). this will hit the database and delete the row with pk=11 in the collection table.

    # to delete multiple objects at once, you can filter them first to get queryset and then call delete().
    collection = Collection.objects.filter(pk__gt=20) # Get a QuerySet of Collections with primary key greater than 5 (does not hit the database yet)
    collection.delete() # Delete the filtered Collections from the database (DELETE operation). this will hit the database and delete all rows with pk>5 in the collection table.
    
    # in one line
    # Collection.objects.filter(pk__gt=10).delete() # Delete Collections with primary key greater than 10 (DELETE operation). this will hit the database and delete all rows with pk>10 in the collection table.



    # Transactions
    # Transactions allow you to group multiple database operations into a single unit of work that either fully succeeds or fully fails.
    # This is useful for maintaining data integrity, especially when performing multiple related operations that must all succeed together.
    # In Django, you can manage transactions using the atomic() context manager or decorator
    
    # always create parent object first before creating child object because of foreign key constraint.
    # with transaction.atomic(): # Start a transaction block (ensures all operations inside either fully succeed or fully fail)
    #     order = Order() # Create a new Order instance (not saved to the database yet)
    #     order.customer_id = 1 # assuming a customer with pk=1 already exists
    #     order.save() # Save the Order to the database (INSERT operation)

    #     order_item = OrderItem() # Create a new OrderItem instance (not saved to the database yet)
    #     order_item.order = order # Set the foreign key to the newly created order
    #     order_item.product_id = 1 # assuming a product with pk=1 already exists
    #     order_item.quantity = 1
    #     order_item.unit_price = 20
    #     order_item.save() # Save the OrderItem to the database (INSERT operation)
    # If any operation inside the atomic block raises an exception, all changes made within the block are rolled back, ensuring data integrity.
    # If all operations succeed, the transaction is committed, and the changes are saved to the database.
    # Tips: if you want make full function atomic, you can use @transaction.atomic decorator on top of the function definition.



    # Executing raw SQL queries
    # In addition to using Django's ORM, you can also execute raw SQL queries directly against the database.
    # This can be useful for complex queries that are difficult to express using the ORM, or for performance optimizations.
    # To execute raw SQL queries, you can use the raw() method of the model manager or the connection object from django.db.
    product = Product.objects.raw('SELECT * FROM store_product') # Execute a raw SQL query to fetch all products. this will return a RawQuerySet which is similar to a regular QuerySet but does not support all the methods of a QuerySet.
    # this will also return queryset but it is not a real queryset. it is a RawQuerySet. so it does not support all the methods of a QuerySet. for example, you cannot use filter(), exclude(), order_by(), etc. on a RawQuerySet. you can only iterate over it or convert it to a list.

    # Tips: use raw SQL queries sparingly and only when necessary, as they can make your code less portable and harder to maintain. always prefer using the ORM whenever possible. use raw SQL queries only for complex queries that cannot be expressed using the ORM or for performance optimizations.

    # Sometime we need to query that dont map to a model. in that case, we can use connection object from django.db to execute raw SQL queries.
    # By this way, you can access database directly without going through a model. this is useful for executing queries that do not map to a specific model or for performing database operations that are not supported by the ORM.
    cursor = connection.cursor() # Get a cursor object to execute raw SQL queries
    cursor.execute('SELECT COUNT(*) FROM store_product') # Execute a raw SQL query to count all products
    cursor.close() # Close the cursor to release database resources

    # best practive is to use with statement to automatically close the cursor after use.
    with connection.cursor() as cursor:
        cursor.execute() 
        # alternatively, you can use callproc() method to call stored procedures.
        # cursor.callproc('stored_procedure_name', [param1, param2, ...
    # even if an exception occurs, the cursor will be closed automatically when exiting the with block.

    # cursor vs raw():
    # cursor provides more flexibility and control over the SQL being executed, while raw() is more convenient for simple queries that map directly to a model.
    # cursor requires manual handling of SQL and result sets, while raw() automatically maps results to model instances.
    # cursor is useful for complex queries or operations that do not fit well with the ORM, while raw() is suitable for straightforward queries that can be expressed in SQL.


    return render(request, 'hello.html', {'name': 'Arafat', 'products': list(cursor)})
