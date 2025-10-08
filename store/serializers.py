from rest_framework import serializers

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
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2) # name of the field in the model is unit_price but we can to expose it as price in the API. so we can change the name here. name does not have to be same as model field name.