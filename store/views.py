from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend # import DjangoFilterBackend for filtering support 
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from store.filters import ProductFilter
from store.pagination import DefaultPagination
from .models import Cart, OrderItem, Product, Collection, Review, CartItem
from .serializers import CartSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer
from rest_framework import status
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

# Example API view function using Django REST Framework (DRF).
# In Django, HTTP communication is handled using HttpRequest (incoming request) and HttpResponse (outgoing response).
# DRF provides its own Request and Response classes, which add features like content negotiation and flexible data handling for APIs.
@api_view()  # Marks this function as a DRF API endpoint, enabling support for various HTTP methods (GET, POST, etc.).
def product_list_test(request):
    # return HttpResponse("OK")  # Standard Django response; not recommended for APIs.
    return Response("OK")  # DRF Response; preferred for APIs as it supports multiple formats (JSON, XML, etc.).
# By adding the @api_view() decorator and using DRF's Response, this function becomes a proper API endpoint.
# These changes also enable DRF's browsable API interface for easier testing and exploration in the browser.



@api_view(['GET', 'POST'])  # Allows only GET and POST requests; other methods return 405 Method Not Allowed.
def product_list__Option_1_method(request):
    if request.method == 'GET':
        # Fetch all products, including related collection objects in a single query for efficiency.
        queryset = Product.objects.select_related('collection').all()
        # Serialize the queryset to native Python datatypes for rendering as JSON or other formats.
        # 'many=True' indicates a list of objects; 'context' passes the request for URL generation.
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Deserialize incoming request data to create a Product instance.
        serializer = ProductSerializer(data=request.data)
        # Validate the data; if invalid, raises a ValidationError and returns 400 Bad Request.
        serializer.is_valid(raise_exception=True)
        # Save the validated data to the database, creating a new Product instance.
        serializer.save()
        # Return the serialized data of the newly created product with a 201 Created status.
        return Response(serializer.data, status=status.HTTP_201_CREATED)



# Class-based views using DRF's APIView:
# - APIView is the base class for all class-based views in Django REST Framework.
# - It provides methods for handling HTTP verbs: get(), post(), put(), delete(), patch(), head(), options(), trace().
# - You can define these methods in your view to handle corresponding HTTP requests.
# - Class-based views improve code organization and reusability, especially for complex endpoints.
# - Inheritance and mixins allow for shared logic and customization across multiple views.

# How requests are processed in class-based views:
# - When a request is made, the as_view() method creates an instance of the view class.
# - The dispatch() method routes the request to the appropriate handler (e.g., get(), post()) based on the HTTP method.
# - Any parameters passed to as_view() are available as attributes on the view instance.

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



# ProductList__Option_3_Mixin_override:
# This view uses DRF's ListCreateAPIView, which combines ListModelMixin and CreateModelMixin.
# - Handles GET requests to list products and POST requests to create new products.
# - Inherits from GenericAPIView, providing features like pagination, filtering, and ordering.
# - Override get_queryset() to customize the queryset (e.g., add select_related for efficiency).
# - Override get_serializer_class() to specify the serializer used for serialization/deserialization.
# - Override get_serializer_context() to pass additional context (e.g., request object) to the serializer.
# - No need to define get() or post() methods; ListCreateAPIView provides them.
# - Setting queryset and serializer_class directly is possible for simple cases; override methods for customization.

class ProductList__Option_3_Mixin_override(ListCreateAPIView):
    def get_queryset(self):
        # Returns all products, using select_related to optimize database queries for related collections.
        return Product.objects.select_related('collection').all()

    def get_serializer_class(self):
        # Specifies the serializer to use for both listing and creating products.
        return ProductSerializer

    def get_serializer_context(self):
        # Passes the request object to the serializer for context (e.g., URL generation).
        return {'request': self.request}



# DRF View Implementation Methods:
# 1. Function-based views using @api_view.
# 2. Class-based views using APIView.
# 3. Class-based views using generics and mixins (override methods for customization).
# 4. Class-based views using generics only (recommended for simplicity).
#
# Method 4 is the most concise and recommended approach for standard CRUD endpoints.
# By directly setting queryset and serializer_class, you avoid boilerplate and gain built-in support for pagination, filtering, and ordering.
# Override get_queryset or get_serializer_class only if you need custom logic.
# Use get_serializer_context to pass extra context (such as the request) to the serializer.

class ProductList__Option_4(ListCreateAPIView):
    queryset = Product.objects.all()  # The queryset for listing and creating products.
    serializer_class = ProductSerializer  # The serializer for both GET and POST requests.

    def get_serializer_context(self):
        # Pass the request object to the serializer for context (e.g., URL generation).
        return {'request': self.request}




@api_view()
def product_detail_manual_check(request, id):
    # Attempts to retrieve a Product by primary key (id).
    # If found, serializes the Product instance and returns it as a JSON response.
    # If not found, returns a 404 Not Found response.
    try:
        product = Product.objects.get(pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
        # Note: Returning HttpResponse(product) would send the string representation of the Product,
        # which is not suitable for APIs. Always serialize before responding.
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



# Handles GET, PUT, and DELETE requests for a single Product instance.
# Uses get_object_or_404 to retrieve the Product by id, returning a 404 response if not found.
@api_view(['GET', 'PUT', 'DELETE'])  # Only allows GET, PUT, and DELETE methods; others return 405 Method Not Allowed.
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)  # Retrieve the product or return 404 if not found.
    if request.method == 'GET':
        serializer = ProductSerializer(product)  # Serialize the product instance.
        return Response(serializer.data)  # Return serialized product data.
    elif request.method == 'PUT':
        # Deserialize and validate incoming data to update the product.
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)  # Raises 400 Bad Request if validation fails.
        serializer.save()  # Update the product in the database.
        return Response(serializer.data)  # Return updated product data.
    elif request.method == 'DELETE':
        # Prevent deletion if the product is associated with any order items.
        if product.orderitems.count() > 0:
            return Response(
                {'error': 'Product cannot be deleted because it is associated with order items.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        product.delete()  # Delete the product from the database.
        return Response(status=status.HTTP_204_NO_CONTENT)  # Indicate successful deletion with no content.



class ProductDetails__generic_way(APIView):
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



# ProductDetails view using DRF generics:
# - Inherits from RetrieveUpdateDestroyAPIView, which provides GET, PUT, and DELETE handlers for a single object.
# - Set queryset and serializer_class to specify the data source and serializer.
# - By default, DRF uses 'pk' as the lookup field, which matches the primary key ('id').
# - Override delete() to prevent deletion if the product is associated with any order items.
class ProductDetails__method_4(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # lookup_field = 'id' # by default, DRF uses 'pk' as the lookup field. here we change it to 'id' to match our URL pattern. if we use 'pk', it will work the same way because 'pk' is an alias for the primary key field, which is 'id' in this case.
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response(
                {'error': 'Product cannot be deleted because it is associated with order items.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
def collection_list__Option_1_function(request):
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



# Option 2: Class-based view using APIView.
# - Handles GET and POST requests for collections.
# - GET: Returns a list of all collections, optionally prefetching related products for efficiency.
# - POST: Creates a new collection from request data.
class CollectionList__Option_2_class(APIView):
    def get(self, request):
        queryset = Collection.objects.prefetch_related('product_set').all()
        # Alternatively, use annotate(product_count=Count('product')) to include product counts.
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Option 3: Class-based view using generics and mixins with method overrides.
# - Inherits from ListCreateAPIView to handle GET (list) and POST (create) requests.
# - get_queryset: Returns collections annotated with product counts for each collection.
# - get_serializer_class: Specifies the serializer to use.
class CollectionList__Option_3_Mixin_override(ListCreateAPIView):
    def get_queryset(self):
        # Annotate each collection with the count of related products.
        return Collection.objects.annotate(product_count=Count('product')).all()

    def get_serializer_class(self):
        return CollectionSerializer


# Option 4: Class-based view using generics only (recommended for simplicity).
# - Inherits from ListCreateAPIView for GET and POST requests.
# - Sets queryset and serializer_class directly for concise implementation.
# - Prefetches related products for efficient queries.
class CollectionList__Opthon_4(ListCreateAPIView):
    queryset = Collection.objects.prefetch_related('product_set').all()
    serializer_class = CollectionSerializer


@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail__method_view(request, pk):
    # Handles GET, PUT, and DELETE requests for a single Collection instance.
    # GET: Returns the collection details.
    # PUT: Updates the collection with provided data.
    # DELETE: Deletes the collection only if it has no related products.
    collection = get_object_or_404(Collection, pk=pk)
    # To include product count in the response, you could annotate the queryset:
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
        # Prevent deletion if the collection contains any products.
        if collection.product_set.count() > 0:
            return Response(
                {'error': 'Collection cannot be deleted because it includes one or more products.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
# Generic class-based view for retrieving, updating, and deleting a Collection.
# Inherits from RetrieveUpdateDestroyAPIView, which provides GET, PUT, and DELETE handlers.
# Uses queryset annotated with product_count for additional context if needed.
# The delete method is overridden to prevent deletion if the collection contains products.
class collection_detail__Option_4(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        # Prevent deletion if the collection contains any products.
        collection = get_object_or_404(Collection, pk=pk)
        if collection.product_set.count() > 0:
            return Response(
                {'error': 'Collection cannot be deleted because it includes one or more products.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





    # ------------------------------------------------------------------------------
    # DRF Views: Function-based, Class-based, and ViewSets
    # ------------------------------------------------------------------------------

    # Django REST Framework (DRF) supports multiple ways to implement API endpoints:
    # 1. Function-based views using @api_view
    # 2. Class-based views using APIView
    # 3. Class-based views using generics and mixins (e.g., ListCreateAPIView, RetrieveUpdateDestroyAPIView)
    # 4. Class-based views using generics only (recommended for standard CRUD operations)

    # For each resource (e.g., Product), you typically need two endpoints:
    # - List & Create (GET, POST)
    # - Retrieve, Update, Delete (GET, PUT, DELETE)
    # These can be implemented as separate functions or classes.

    # As your API grows, managing many separate views for each resource can become unwieldy.
    # ------------------------------------------------------------------------------
    # ViewSets:
    # ------------------------------------------------------------------------------
    # - ViewSets group related actions (list, create, retrieve, update, delete) for a resource into a single class.
    # - This improves code organization and maintainability.
    # - Routers can be used with ViewSets to automatically generate URL patterns, reducing boilerplate.
    # - ViewSets are recommended for large or complex APIs.



# Previously, separate views handled listing/creating products and retrieving/updating/deleting a product.
# Now, these are combined into a single ViewSet, which provides all CRUD endpoints for the Product resource.
# This approach is more organized and maintainable.
# ModelViewSet provides default implementations for all standard CRUD operations.
# For API endpoints in urls.py, you can use a router to automatically generate URL patterns for this ViewSet.

# Handles all actions (list, create, retrieve, update, delete) for the Product resource.
# in generic way, for delete we override the delete method that actually calls destroy method. but in ViewSet we override destroy method directly.
class ProductViewSet(ModelViewSet):  # Naming convention: <Resource>ViewSet, e.g., ProductViewSet
    queryset = Product.objects.all()  # Queryset used for all actions unless overridden.
    serializer_class = ProductSerializer  # Serializer used for all actions unless overridden.

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  # Enable filtering support using DjangoFilterBackend. SearchFilter added for search functionality. here OrderingFilter is also added to enable ordering functionality.
    # filterset_fields = ['collection_id', 'unit_price']  # Allow filtering products by collection_id via query parameters.
    filterset_class = ProductFilter # instead of filterset_fields, we use filterset_class to specify a custom FilterSet class.
    search_fields = ['title', 'description'] # enable search functionality on title and description fields.
    ordering_fields = ['unit_price', 'last_update'] # enable ordering functionality on unit_price and last_update fields.
    # by usiing DjangoFilterBackend, it adds filtering support to the ViewSet automatically. also in web it adds filtering UI in the browsable API.

    # we can set this pagination_class in settings.py globally for the entire project. but if we want to set it for this ViewSet only, we can uncomment the line below.
    # pagination_class = PageNumberPagination  # Enable pagination using page number pagination.
    pagination_class = DefaultPagination # here we use our custom pagination class defined in pagination.py so that we can easily change the page size in one place.
    # parser_classes = LimitOffsetPagination # Enable pagination using limit-offset pagination. here offset is the starting point and limit is the number of items to return.

    # Note: if we want to filter products based on collection_id from query parameters, we can do it in two ways:
    # 1. Using DjangoFilterBackend as shown above. This is the recommended way for simple filtering.
    # 2. Manually overriding get_queryset method as shown below.
    
    # # Override get_queryset to filter products by collection_id if provided in query parameters.
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id') # get collection_id from query parameters. if not provided, it will be None. here get method is used to avoid KeyError. when not provided, it returns None.
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)

    #     return queryset
    
    def get_serializer_context(self):
        # Passes the request to the serializer for generating full URLs (e.g., HyperlinkedRelatedField).
        return {'request': self.request}
        
    # Efficient product deletion check:
    # There are two ways to check if a product is associated with order items before deletion:
    # 1. Fetch the Product instance and check its related orderitems count.
    # 2. Directly query the OrderItem model for any items referencing the product (recommended for efficiency).
    # This method uses the second approach to avoid unnecessary database fetches.
    def destroy(self, request, *args, **kwargs):
        # product = get_object_or_404(Product, pk=kwargs['pk']) 
        # if product.orderitems.count() > 0:
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0: 
            return Response(
                {'error': 'Product cannot be deleted because it is associated with order items.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().destroy(request, *args, **kwargs)


# ViewSet for managing Collection resources.
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer_class = CollectionSerializer

    # Override destroy to prevent deletion if the collection has related products.
    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if collection.product_set.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
        return super().destroy(request, *args, **kwargs)




class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all() 
    
    # # here we want to filter reviews based on the product they belong to. so we will override get_queryset method instead of setting queryset attribute.
    # we will get product_pk from the URL. so we will filter reviews based on product_id which is equal to product_pk from the URL.
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']} # 'product_pk' comes from the nested router's URL pattern. url has two parameters: product_pk and pk. here we pass product_pk to the serializer context so that we can use it in the serializer to associate the review with the correct product.



# This ViewSet exposes only the "create" action (POST /carts/) by using CreateModelMixin + GenericViewSet.
# We intentionally do not provide list/retrieve/update/destroy at the top-level cart endpoint to avoid exposing all cart IDs.
# Cart items (line items) should be managed via separate endpoints (e.g., CartItem viewset or nested routes).
# The CartSerializer is expected to validate nested items and create the Cart and its items atomically.
# To add retrieve/update/delete for individual carts, include the corresponding mixins (RetrieveModelMixin,
# UpdateModelMixin, DestroyModelMixin) or use ModelViewSet with appropriate permission checks.
# - Purpose: expose only the create action (POST /carts/) via CreateModelMixin + GenericViewSet.
# - Expectations: CartSerializer validates nested items and creates Cart + LineItems atomically.

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet): # here we use CreateModelMixin to provide only the create action and GenericViewSet as the base class for the ViewSet.

    queryset = Cart.objects.prefetch_related('items__product').all() # prefetch related items and products to avoid N+1 query problem when retrieving a cart along with its items and their associated products. here item__product __ is used to traverse the relationship from Cart to CartItem (items) and then to Product (product). but for foreign key relationships, select_related is preferred. however, since Cart to CartItem is a one-to-many relationship, we use prefetch_related for that part.
    serializer_class = CartSerializer
























# Tips: use below SQL command to reset the primary key sequence in Postgres if you manually delete all rows from a table. this will ensure that the next inserted row will have the correct primary key value.
# SELECT setval(pg_get_serial_sequence('store_product', 'id'), (SELECT MAX(id) FROM store_product) + 1);
