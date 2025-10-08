from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from rest_framework import status

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
def product_list(request):
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
        serializer.validated_data # this contains the validated data after passing all validation checks. we can use this data to create or update a Product instance.
        return Response('ok')


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
@api_view()
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id) # get product from database or return 404 if not found. this also returns a error response on response if product not found. 
    serializer = ProductSerializer(product) # serialize the product instance to native python datatypes
    return Response(serializer.data) # return the serialized data as a response


@api_view()
def collection_detail(request, pk):
    return Response(f"Collection id : {pk}")