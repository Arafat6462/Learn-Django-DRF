from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter
from pprint import pprint
from django.urls import include

# Create a router instance. DefaultRouter provides automatic URL routing for viewsets, including a default API root view and format suffix patterns.
router = DefaultRouter()

# Register ProductViewSet and CollectionViewSet with the router. The first argument is the URL prefix, and the second is the viewset class.
# This automatically generates standard RESTful routes for each viewset.
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)

# Print the generated URLs for debugging purposes.
pprint(router.urls)

# Note:
# - SimpleRouter generates standard RESTful routes for registered viewsets (list, create, retrieve, update, partial_update, destroy).
# - DefaultRouter extends SimpleRouter by adding a default API root view and format suffix patterns.
# - Use DefaultRouter for more features; use SimpleRouter for a minimal setup.

# Example of manually defined URL patterns (commented out):
# urlpatterns_manually = [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/', views.ProductDetails.as_view()),
#     path('collections', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.collection_detail.as_view(), name='collection-detail'),
# ]
# These manual patterns are replaced by router-generated routes for simplicity and maintainability.

# Use the router-generated URLs as the urlpatterns.
urlpatterns = [
    path('', include(router.urls)),
]

