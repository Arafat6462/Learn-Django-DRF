from decimal import Decimal
from rest_framework import serializers
from store.models import Product

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

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255) # we add all this fields manually again because when user sends data to create a new product, we need to validate these fields and convert them to python datatypes
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price') # name of the field in the model is unit_price but we can to expose it as price in the API. so we can change the name here. name does not have to be same as model field name. here source='unit_price' tells the serializer to use the unit_price field from the model for this price field.
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax') # this field is not in the model. we are adding this field to the serializer only. SerializerMethodField is a read-only field that gets its value by calling a method on the serializer class. method_name specifies the name of the method to call to get the value for this field.

    def calculate_tax(self, product: Product): # Here :Product is a type hint indicating that the product parameter should be an instance of the Product model. this helps with code readability and can assist IDEs in providing better autocompletion and type checking.
        return product.unit_price * Decimal(1.1) # Decimal is used to avoid floating point precision issues.