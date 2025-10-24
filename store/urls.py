from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from pprint import pprint
from django.urls import include

# Create a router instance. DefaultRouter provides automatic URL routing for viewsets, including a default API root view and format suffix patterns.
router_old = DefaultRouter() # this is drf's router
router = routers.DefaultRouter() # we are nested routers instead of drf's rou

# Register ProductViewSet and CollectionViewSet with the router. The first argument is the URL prefix, and the second is the viewset class.
# This automatically generates standard RESTful routes for each viewset.
router.register('products', views.ProductViewSet, basename='products') # 'products' is the URL prefix for ProductViewSet
router.register('collections', views.CollectionViewSet)

# Print the generated URLs for debugging purposes.
# pprint(router.urls)

# Note:
# - SimpleRouter generates standard RESTful routes for registered viewsets (list, create, retrieve, update, partial_update, destroy).
# - DefaultRouter extends SimpleRouter by adding a default API root view and format suffix patterns.
# - Use DefaultRouter for more features; use SimpleRouter for a minimal setup.

# Example of manually defined URL patterns (commented out):
urlpatterns_manually_way = [
    # path('products/', views.ProductList.as_view()),
    # path('products/<int:pk>/', views.ProductDetails.as_view()),
    # path('collections', views.CollectionList.as_view()),
    # path('collections/<int:pk>/', views.collection_detail.as_view(), name='collection-detail'),
]
# These manual patterns are replaced by router-generated routes for simplicity and maintainability.


# we created parent router above. Now we will create a child router for nested routes.
# Here, we create a nested router for reviews under products.
# /domains/{domain_pk}/nameservers/{pk} <- Specific nameserver from {pk}, of domain from {domain_pk}
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product') # 'products' is the prefix of the parent router, and 'product' is the lookup field used in the URL. here three parameters are 1. parent router, 2. prefix of the parent router, 3. lookup field for the child router.
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews') # 'reviews' is the prefix for the nested route, and ReviewViewSet is the viewset handling requests to this nested route. basename is used to name the URL patterns.

# Use the router-generated URLs as the urlpatterns.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)), # include the nested router URLs
]

