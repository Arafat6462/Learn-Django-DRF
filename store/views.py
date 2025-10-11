from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer
from rest_framework import status
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.generics import ListCreateAPIView

# view function takes input as request and returns response
"""
In Django, there are two main classes for handling HTTP communication: `HttpRequest` and `HttpResponse`.
The `HttpRequest` class represents the incoming request from the client, while the `HttpResponse` class is used to construct the response sent back to the client.
Note: Django REST Framework (DRF) introduces its own `Request` and `Response` classes, which provide additional features for building RESTful APIs, such as content negotiation and more flexible data handling.
"""
@api_view() # DRF decorator to specify that this view is an API endpoint so it can handle various HTTP methods like GET, POST, etc.
def product_list_test(request):
    # return HttpResponse("OK") # Basic Django response. this is not suitable for APIs. 
    return Response("OK") # DRF response, suitable for APIs. it can handle various data formats like JSON, XML, etc.
# Note: only two changes are made here. 1. @api_view() decorator is added. 2. HttpResponse is replaced with Response. with these two changes, this view function is now ready to serve as an API endpoint.
# This two changes also makes browserable API. you can visit this endpoint in browser and see the response in a nice format. 

@api_view(['GET', 'POST']) # specify allowed HTTP methods for this view. if a request with a different method is made, DRF will return a 405 Method Not Allowed response automatically. by default 'GET' are allowed.f
def product_list__Option_1_method(request):
    if request.method == 'GET':
        queryset = Product.objects.select_related('collection').all() # get all products from database, it returns a queryset of Product instances. select_related is used to optimize the query by fetching related collection objects in the same query using a SQL join. this avoids additional queries when accessing the collection attribute of each product.
        serializer = ProductSerializer(queryset, many=True, context={'request':request}) # convert complex data (queryset of Product instances) to native python datatypes using serializer, so that it can be easily rendered to JSON, XML, etc. many=True means we are serializing a list of objects. context is used to pass additional context to the serializer. here we pass the request object so that HyperlinkedRelatedField can generate full URLs.
        return Response(serializer.data) # return the serialized data as a response, DRF Response class takes care of rendering the data to JSON or other formats. it use jsonrenderer by default to convert python datatypes to JSON.
    
   # for POST request: Deserialization: converting data from JSON (or other formats) to complex data types (like Django models).
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data) # deserialize the incoming data to a Product instance. request.data contains the parsed data from the request body. it can handle various content types like JSON, form data, etc.
        # for serialization we pass the instance or queryset to the serializer. for deserialization we pass the data to the serializer.
       
        # if serializer.is_valid(): # validate the incoming data against the serializer's validation rules. if the data is valid, we can proceed to save it.
        #     serializer.validated_data # this contains the validated data after passing all validation checks. we can use this data to create or update a Product instance.
        #     return Response('ok')
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # more concise way to write the above code:
        serializer.is_valid(raise_exception=True) # if the data is not valid, it will raise a ValidationError which DRF will catch and return a 400 Bad Request response with the error details.
        serializer.save() # save the validated data to create a new Product instance in the database. this method calls create() or update() method of the serializer internally.
        # serializer.validated_data # this contains the validated data after passing all validation checks. we can use this data to create or update a Product instance.
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Class based views
# APIView is a base class for all class based views in DRF. it provides the core functionality for handling HTTP methods and rendering responses. 
# we can define methods like get(), post(), put(), delete() etc. to handle the corresponding HTTP methods.
# Class based views provide better organization and reusability of code. we can use inheritance and mixins to create reusable components. they also provide better support for complex views with multiple HTTP methods and actions.

# how class method calls work:
# when a request is made to a class based view, the as_view() method is called first. this method creates an instance of the view class and then calls the dispatch() method. the dispatch() method is responsible for routing the request to the appropriate method (get(), post(), put(), delete(), etc.) based on the HTTP method of the request. it also handles any authentication, permissions, and throttling that may be applied to the view.
# available methods in APIView class: get(), post(), put(), delete(), patch(), head(), options(), trace() 
# parameters passed to as_view() method are available in the view instance as attributes. for example, if we pass a parameter 'id' to as_view() method, we can access it in the view instance as self.id.
class ProductList__Option_2_class(APIView): 
    def get(self, request): 
        queryset = Product.objects.select_related('collection').all() 
        serializer = ProductSerializer(queryset, many=True, context={'request':request}) 
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# using mixins to simplify the above code. mixins provide reusable components that can be combined to create complex views. here we use ListModelMixin and CreateModelMixin to handle GET and POST requests respectively.
# Moreover, we can use generics to further simplify the code. generics provide pre-built views for common use cases like listing, creating, retrieving, updating, and deleting objects. here we use ListCreateAPIView which combines ListModelMixin and CreateModelMixin to handle both GET and POST requests.
# We can use ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView, etc. for specific use cases.
# generics also provide built-in support for pagination, filtering, and ordering. we can easily add these features to our views by setting the appropriate attributes.
# Note: when using generics, we need to set the queryset and serializer_class attributes to specify the data source and serializer to be used
class ProductList__Option_3_Mixin_override(ListCreateAPIView): # combines ListModelMixin and CreateModelMixin. ApiView is the base class for all class based views in DRF. we can also use GenericAPIView as the base class which provides more functionality like pagination, filtering, etc.
# we can override the following methods to customize the behavior of the view: else we can directly set the attributes queryset and serializer_class.
    
    def get_queryset(self): # we override get_queryset() method to customize the queryset. this method is called by the ListModelMixin to get the data to be listed.
        return Product.objects.select_related('collection').all()

    def get_serializer_class(self): # we override get_serializer_class() method to customize the serializer class. this method is called by the CreateModelMixin to get the serializer to be used for deserialization.
        return ProductSerializer

    def get_serializer_context(self): # we override get_serializer_context() method to customize the context passed to the serializer. this method is called by both ListModelMixin and CreateModelMixin to get the context to be passed to the serializer.
        return {'request': self.request} # we pass the request

    # Note: with get_queryset(), get_serializer_class(), this will works for both GET and POST requests. so we don't need to define separate methods for GET and POST like in the previous example. because ListCreateAPIView already has the logic to handle both GET and POST requests using the appropriate mixins.
    # ListCreateAPIView already has get() and post() methods defined which call the appropriate mixin methods to handle the requests.


# Good News: we can further simplify the above code by directly setting the queryset and serializer_class attributes. this is possible because we are not doing any complex logic in get_queryset() and get_serializer_class() methods. so we can directly set the attributes instead of overriding the methods.
# For view we can use.
# 1. Method 1: function based view using @api_view() decorator.
# 2. Method 2: class based view using APIView class.
# 3. Method 3: class based view using mixins and generics.
# 4. Method 4: class based view using generics only (simplest and most recommended way).
# Method 4 is the most concise and recommended way to create views in DRF. it provides the same functionality as Method 3 but with less code. it also provides built-in support for pagination, filtering, and ordering. we can easily add these features to our views by setting the appropriate attributes.
# we can use Method 1 for simple views with only one or two
class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related('collection').all() # set the queryset to be used for listing products. this will be used by ListModelMixin to get the data to be listed. if we need to filter the queryset based on some criteria, we can override get_queryset() method instead.
    serializer_class = ProductSerializer # set the serializer class to be used for serialization and deserialization. this will be used by both ListModelMixin and CreateModelMixin to get the serializer to be used. if we need to use different serializers for GET and POST requests, we can override get_serializer_class() method instead.
    
    def get_serializer_context(self): # we override get_serializer_context() method to customize the context passed to the serializer. this method is called by both ListModelMixin and CreateModelMixin to get the context to be passed to the serializer.
        return {'request': self.request} # we pass the request




@api_view()
def product_detail_manual_check(request, id):
    try:
        product = Product.objects.get(pk=id) # get product from database, it returns a Product instance. pk means primary key. here pk is id.
        serializer = ProductSerializer(product) # convert complex data (Product instance) to native python datatypes using serializer, so that it can be easily rendered to JSON, XML, etc.
        return Response(serializer.data) # return the serialized data as a response, DRF Response class takes care of rendering the data to JSON or other formats. it use jsonrenderer by default to convert python datatypes to JSON.
        # return HttpResponse(product) # This will return the string representation of the Product instance, which is not suitable for APIs. We need to serialize it first before sending as a response.
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND) # return 404 if product not found

# Using get_object_or_404 shortcut to simplify the above code. it tries to get the object and if not found, it raises a 404 error automatically.
@api_view(['GET', 'PUT', 'DELETE']) # specify allowed HTTP methods for this view. if a request with a different method is made, DRF will return a 405 Method Not Allowed response automatically. by default 'GET' are allowed. for 'DELETE' DRF add a delete button on web interface. and for 'PUT' it adds a form to update the object.
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id) # get product from database or return 404 if not found. this also returns a error response on response if product not found. 
    if request.method == 'GET':
        serializer = ProductSerializer(product) # serialize the product instance to native python datatypes
        return Response(serializer.data) # return the serialized data as a response
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data) # deserialize the incoming data to update the existing Product instance. request.data contains the parsed data from the request body. it can handle various content types like JSON, form data, etc. thsi will call ModelSerializer's update() method internally because we are passing an instance (product) to the serializer along with the data.
        serializer.is_valid(raise_exception=True) # validate the incoming data against the serializer's validation rules. if the data is valid, we can proceed to save it. if the data is not valid, it will raise a ValidationError which DRF will catch and return a 400 Bad Request response with the error details.
        serializer.save() # save the validated data to update the existing Product instance in the database. this method calls create() or update() method of the serializer internally.
        return Response(serializer.data) # return the updated serialized data as a response
    elif request.method == 'DELETE':
        if product.orderitems.count() > 0: # check if the product is associated with any order items. if yes, we cannot delete it. here orderitems is the related_name we added in OrderItem model's ForeignKey to Product model. if we did not add related_name, it would be orderitem_set by default.
            return Response({'error': 'Product cannot be deleted because it is associated with order items.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) # return 405 Method Not Allowed response with error message. in dict you can add any key value pairs you want. here we add an 'error' key with the error message as value.
        product.delete() # delete the product instance from the database
        return Response(status=status.HTTP_204_NO_CONTENT) # return 204 No Content response to indicate successful deletion. 204 means the request was successful but there is no content to send in the response.


class ProductDetails(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
     
    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with order items.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        queryset = Collection.objects.prefetch_related('product_set').all() 
        # queryset = Collection.objects.annotate(product_count=Count('product'))
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    # collection = get_object_or_404(Collection.objects.annotate(product_count=Count('product')), pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        if collection.product_set.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# Tips: use below SQL command to reset the primary key sequence in Postgres if you manually delete all rows from a table. this will ensure that the next inserted row will have the correct primary key value.
# SELECT setval(pg_get_serial_sequence('store_product', 'id'), (SELECT MAX(id) FROM store_product) + 1);
