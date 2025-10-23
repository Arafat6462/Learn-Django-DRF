from django_filters import FilterSet
from .models import Product

# Define a custom FilterSet for the Product model to enable advanced filtering options. 
class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt'],
        }

