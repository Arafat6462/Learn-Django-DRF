from django.urls import path
from . import views

urlpatterns = [
    # Define your URL patterns here
    path('products/', views.product_list),
    path('products/<int:id>/', views.product_detail), # Dynamic URL pattern with product ID, passed as argument to view function views.product_detail. also note that id is an integer.
    path('collections', views.collection_list),
    path('collections/<int:pk>/', views.collection_detail, name='collection-detail'), # named URL pattern for HyperlinkedRelatedField in ProductSerializer. here pk is used instead of id because DRF uses pk by default for lookup fields.  name='collection-detail' is used to reference this URL pattern in serializers.py for HyperlinkedRelatedField.
]

