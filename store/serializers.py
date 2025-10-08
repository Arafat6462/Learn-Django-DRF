from decimal import Decimal
from rest_framework import serializers
from store.models import Product, Collection

# DRF serializers are responsible for transforming complex data (like Django models) into native Python datatypes. This makes it easy to render data as JSON, XML, etc.
# Serializers also handle deserialization: they validate and transform incoming data (such as JSON from an API request) back into Python objects or Django models.

# What is a Serializer?
# - A serializer defines the structure of data that will be sent to or received from the API. 
# - It specifies which fields are exposed, how they are validated, and how they are converted.
# - Serializers can be used for both input (deserialization) and output (serialization).
# Why use Serializers?
# - To control which fields are visible in the API.
# - To add custom validation logic for incoming data.
# - To transform data formats (e.g., dates, nested objects).
# - To convert between Django models and JSON (or other formats).
# Types of Serializers:
# 1. serializers.Serializer: Manually declare each field. More control, but more verbose.
# 2. serializers.ModelSerializer: Automatically generates fields from a Django model. Less code, but less control.
#
# How does it work?
# - When sending data to the client (serialization), the serializer converts model instances to Python datatypes, then to JSON.
# - When receiving data from the client (deserialization), the serializer validates and converts JSON to Python datatypes, and optionally to model instances.

class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255) # we add all this fields manually again because when user sends data to create a new product, we need to validate these fields and convert them to python datatypes
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price') # name of the field in the model is unit_price but we can to expose it as price in the API. so we can change the name here. name does not have to be same as model field name. here source='unit_price' tells the serializer to use the unit_price field from the model for this price field.
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax') # this field is not in the model. we are adding this field to the serializer only. SerializerMethodField is a read-only field that gets its value by calling a method on the serializer class. method_name specifies the name of the method to call to get the value for this field.
    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all()) # this field represents the relationship between Product and Collection models. it will show the primary key (id) of the related collection. queryset is required for writable fields to specify which objects are valid.
    collection_string = serializers.StringRelatedField(source='collection') # this field will show the string representation of the related collection. it uses the __str__ method of the Collection model. if we don't specify source, it will look for a field named collection_string in the model which does not exist. and in views.py, we use select_related to optimize the query and avoid additional queries when accessing the collection attribute of each product. to avoid n+1 query problem.
    nested_object_collection = CollectionSerializer(source='collection') # nested serializer to show all fields of the related collection. here source='collection' tells the serializer to use the collection field from the model for this nested_collection field.
    # Note: Sometimes after adding source, DRF shows queryset error. just restart the server to fix it.

    collection_link = serializers.HyperlinkedRelatedField( # new field added to show link to related collection
        source='collection', # source specifies which attribute on the object should be used to populate this field.
        queryset=Collection.objects.all(), # queryset is required for writable fields to specify which objects are valid.
        view_name='collection-detail' # view_name specifies the name of the view that should be used to generate the URL for the related object. this view should be defined in urls.py
    )


    def calculate_tax(self, product: Product): # Here :Product is a type hint indicating that the product parameter should be an instance of the Product model. this helps with code readability and can assist IDEs in providing better autocompletion and type checking.
        return product.unit_price * Decimal(1.1) # Decimal is used to avoid floating point precision issues.