from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# view function takes input as request and returns response
"""
In Django, there are two main classes for handling HTTP communication: `HttpRequest` and `HttpResponse`.
The `HttpRequest` class represents the incoming request from the client, while the `HttpResponse` class is used to construct the response sent back to the client.
Note: Django REST Framework (DRF) introduces its own `Request` and `Response` classes, which provide additional features for building RESTful APIs, such as content negotiation and more flexible data handling.
"""
@api_view() # DRF decorator to specify that this view is an API endpoint so it can handle various HTTP methods like GET, POST, etc.
def product_list(request):
    # return HttpResponse("OK") # Basic Django response. this is not suitable for APIs. 
    return Response("OK") # DRF response, suitable for APIs. it can handle various data formats like JSON, XML, etc.
# Note: only two changes are made here. 1. @api_view() decorator is added. 2. HttpResponse is replaced with Response. with these two changes, this view function is now ready to serve as an API endpoint.
# This two changes also makes browserable API. you can visit this endpoint in browser and see the response in a nice format. 

@api_view()
def product_detail(request, id):
    return Response(id)  # DRF response with product ID