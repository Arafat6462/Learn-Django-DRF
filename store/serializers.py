from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from store.models import Cart, CartItem, Product, Collection, Review, Customer, Order, OrderItem

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

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
        # fields = '__all__' # This will include all fields from the model in the
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    product_count = serializers.SerializerMethodField(method_name='get_product_count') # custom field to show the number of products in the collection. SerializerMethodField is a read-only field that gets its value by calling a method on the serializer class. method_name specifies the name of the method to call to get the value for this field.

    def get_product_count(self, collection: Collection):
        return collection.product_set.count() # returns the number of products in the collection. count() executes a SQL COUNT query to get the number of related Product instances for the given Collection instance.
    
    # product_count = serializers.IntegerField() # if we use annotate in views.py, we can use IntegerField here to avoid n+1 query problem.


class ProductSerializerV2(serializers.Serializer):
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
    # Note: there are 4 ways to represent relationships in serializers:
    # 1. PrimaryKeyRelatedField: shows the primary key (id) of the related object.
    # 2. StringRelatedField: shows the string representation of the related object.
    # 3. Nested Serializer: shows all fields of the related object using another serializer.
    # 4. HyperlinkedRelatedField: shows a hyperlink to the related object using a URL.

    def calculate_tax(self, product: Product): # Here :Product is a type hint indicating that the product parameter should be an instance of the Product model. this helps with code readability and can assist IDEs in providing better autocompletion and type checking.
        return product.unit_price * Decimal(1.1) # Decimal is used to avoid floating point precision issues.


# ModelSerializer is a shortcut that automatically creates a serializer class based on a Django model.
# so far we have used serializers.Serializer which requires us to define all fields manually. seems repetitive the same fields in two places (model and serializer). to avoid this, we can use ModelSerializer which automatically generates fields based on the model.
# Serializers vs ModelSerializers:
# - Serializers: More control, manually define each field. Good for complex or non-model data.
# - ModelSerializers: Less code, automatically generates fields from model. Good for simple CRUD operations.
# How does ModelSerializer work?
# - It introspects the model to determine the fields and their types.
# - You can still add custom fields and methods as needed.
# - You can specify which fields to include or exclude using the Meta class.
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection'] # specify the fields to be included in the serialized output. 
        # fields = '__all__' # This will include all fields from the model in the serialized output.
        # Note: Using '__all__' is convenient but can expose sensitive fields unintentionally. It's often better to explicitly list the fields you want to expose. if later any new field is added to the model, it will be automatically included in the serializer output if we use '__all__'. this may not be desirable in all cases.

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax') # adding custom field to the serializer. this field is not in the model. we are adding this field to the serializer only. SerializerMethodField is a read-only field that gets its value by calling a method on the serializer class. method_name specifies the name of the method to call to get the value for this field.

    def calculate_tax(self, product: Product): # Here :Product is a type hint indicating that the product parameter should be an instance of the Product model. this helps with code readability and can assist IDEs in providing better autocompletion and type checking.
        return product.unit_price * Decimal(1.1) # Decimal is used to avoid floating point precision issues.
    
    # # Override create method of ModelSerializer. this method is called when we call serializer.save() in views.py for creating a new Product instance.
    # def create(self, validated_data): # override create method to add custom behavior during creation of a new Product instance. validated_data contains the validated data after passing all validation checks.
    #     # return super().create(validated_data) # call the parent class's create method to perform the actual creation of the Product instance.
    #     product = Product(**validated_data) # create a new Product instance using the validated data. **validated_data unpacks the dictionary into keyword arguments.
    #     product.other_field = 'default value' # set a default value for other_field which is not provided by the user.
    #     product.save() # save the Product instance to the database.
    #     return product # return the created Product instance.
    
    # # Override update method of ModelSerializer. this method is called when we call serializer.save() in views.py for updating an existing Product instance.
    # def update(self, instance, validated_data): # override update method to add custom behavior during update of an existing Product instance. instance is the existing Product instance to be updated. validated_data contains the validated data after passing all validation checks.
    #     # return super().update(instance, validated_data) # call the parent class's update method to perform the actual update of the Product instance.
    #     instance.unit_price = validated_data.get('unit_price') # update the unit_price field of the instance with the new value from validated_data. if unit_price is not provided in validated_data, it will keep its current value.
    #     instance.save() # save the updated Product instance to the database.
    #     return instance # return the updated Product instance.


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id'] # get product_id from the serializer context. we pass product_id to the serializer context in views.py in ReviewViewSet's get_serializer_context method.
        return Review.objects.create(product_id=product_id, **validated_data) # create a new Review instance associated with the given product_id. **validated_data unpacks the dictionary into keyword arguments.


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer() # nested serializer to show product details in the cart item
    total_price = serializers.SerializerMethodField() # custom field to show total price of the cart item (quantity * unit_price). SerializerMethodField is a read-only field that gets its value by calling a method on the serializer class. by default, it looks for a method named get_<field_name> to get the value for this field. 
    
    def get_total_price(self, cart_item:CartItem): # method to calculate total price of the cart item. Here :CartItem is a type hint indicating that the cart_item parameter should be an instance of the CartItem model. this helps with code readability and can assist IDEs in providing better autocompletion and type checking. method name is important here. it should be get_total_price to match the field name total_price.
        return cart_item.quantity * cart_item.product.unit_price # calculate total price by multiplying quantity with unit_price of the product. here cart_item.product is the related Product instance for the CartItem instance.

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price'] # here total_price is a custom field added to show the total price of the cart item (quantity * unit_price).


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True) # uuid is the primary key field for Cart model. we set read_only=True because we don't want the user to provide this value when creating a new cart. it will be generated automatically.
    items = CartItemSerializer(many=True, read_only=True) # items is the reverse relationship from CartItem to Cart. we will define CartItemSerializer to show the items in the cart. many=True indicates that there can be multiple items in the cart. Read-only because we don't want the user to provide this value when creating a new cart. items will be added separately.
    total_price = serializers.SerializerMethodField() # custom field to show total price of the cart (sum of total price of all cart items). SerializerMethodField is a read-only field that gets its value by calling a method on the serializer class. by default, it looks for a method named get_<field_name> to get the value for this field.

    def get_total_price(self, cart:Cart): # method to calculate total price of the cart. Here :Cart is a type hint indicating that the cart parameter should be an instance of the Cart model. this helps with code readability and can assist IDEs in providing better autocompletion and type checking. method name is important here. it should be get_total_price to match the field name total_price.
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price'] # Items is the reverse relationship from CartItem to Cart. we will define CartItemSerializer to show the items in the cart.


# Above CartSerializer not used for adding items to cart. we need a separate serializer for that.
# because when adding an item to the cart, we only need product_id and quantity from the user. we don't need to show the entire product details or total price.
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField() # product_id is the foreign key field to Product model. we use product_id instead of product to allow the user to provide the product id when adding an item to the cart.

    def validate_product_id(self, value): # custom validator for product_id field to check if the product with the given id exists.
        if not Product.objects.filter(pk=value).exists(): # check if a product with the given id exists in the database.
            raise serializers.ValidationError('No product with the given id was found.') # raise validation error if product does not exist.
        return value # return the validated value if product exists.

    # here we override the save method to add custom behavior when adding an item to the cart.
    def save(self, **kwargs):
        cart_id = self.context['cart_id'] # get cart_id from the serializer context. we pass cart_id to the serializer context in views.py in CartItemViewSet's get_serializer_context method.
        product_id = self.validated_data['product_id'] # get product_id from the validated data. this is the data provided by the user after passing all validation checks.
        quantity = self.validated_data['quantity'] # get quantity from the validated data.

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id) # check if the cart item already exists in the cart for the given product_id.
            cart_item.quantity += quantity # if it exists, increment the quantity by the provided quantity.
            cart_item.save() # save the updated cart item to the database.
            self.instance = cart_item # set the instance attribute to the updated cart item. this is important for the serializer to return the updated cart item after saving.

        except CartItem.DoesNotExist:
            # CartItem.objects.create(cart_id=cart_id, product_id=product_id, quantity=quantity) # if it does not exist, create a new cart item with the provided cart_id, product_id and quantity.
            self.instance = CartItem.objects.create(**self.validated_data, cart_id=cart_id) # alternative way to create a new cart item using unpacking operator. here we unpack the validated_data dictionary into keyword arguments and add cart_id as well.

        return self.instance # return the created or updated cart item instance.

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity'] # product_id is the foreign key field to Product model. we use product_id instead of product to allow the user to provide the product id when adding an item to the cart.


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity'] # only quantity can be updated when updating a cart item.


class CustomerSerializer(serializers.ModelSerializer):
    # if we don't specify user_id here, DRF will not include it in the serialized output by default.
    user_id = serializers.IntegerField(read_only=True) # read_only=True because we don't want the user to provide this value when creating or updating a customer. it will be set automatically based on the authenticated user.

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership'] 


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer() # nested serializer to show product details in the order item

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) # specify the reverse relation name (default <model>_set) if no related_name is set on the OrderItem FK
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    with transaction.atomic(): # ensure that the entire order creation process is atomic. if any part fails, the entire transaction will be rolled back to maintain data integrity.
        cart_id = serializers.UUIDField()

        def validate_cart_id(self, cart_id):
            if not Cart.objects.filter(pk=cart_id).exists():
                raise serializers.ValidationError('No cart with the given id was found.')
            if CartItem.objects.filter(cart_id=cart_id).count() == 0:
                raise serializers.ValidationError('The cart is empty.')
            return cart_id


        def save(self, **kwargs):
            cart_id = self.validated_data['cart_id']

            customer = Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order = order, 
                    product=item.product, 
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            return order