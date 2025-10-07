from django.urls import path
from . import views

urlpatterns = [
    # Define your URL patterns here
    path('products/', views.product_list),
    path('products/<int:id>/', views.product_detail), # Dynamic URL pattern with product ID, passed as argument to view function views.product_detail. also note that id is an integer.
]

