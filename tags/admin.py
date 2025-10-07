from django.contrib import admin  
from tags.models import Tag

# Register your models here.
@admin.register(Tag)
class TaggedItemAdmin(admin.ModelAdmin):
    search_fields = ['lable'] # to search tags by their label in the admin interface.