from django.contrib import admin
from store.models import Product
from tags.models import TaggedItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from store.admin import ProductAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import User
# Register your models here.

# Register the custom User model with the admin site
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )

class TagInline(GenericTabularInline): # this is used to display the related tags of a product in the product detail view. it is a tabular inline view.
    model = TaggedItem # the model to be displayed in the inline view. here, TaggedItem is the model that has a generic foreign key to the Product model. it is a reverse relationship.
    autocomplete_fields = ['tag'] # this will add a search box to the tag field in the inline form view. it is useful when there are a lot of tags.
    extra = 1 # number of extra forms to display in the inline view. here, we are displaying 1 extra form.
    min_num = 1 # minimum number of forms to display in the inline view. here, we are setting it to 1 to ensure that at least one tag is added.


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline] # to display the related tags of a product in the product detail view.

admin.site.unregister(Product) # unregister the existing Product admin
admin.site.register(Product, CustomProductAdmin) # register the Product model with the custom ProductAdmin