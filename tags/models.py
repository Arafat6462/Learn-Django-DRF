from django.db import models

from store.models import Product
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Creating a custom manager for TaggedItem model
class TaggedItemManager(models.Manager):
    def get_tags_for(self, obj_type, obj_id):
        content_type = ContentType.objects.get_for_model(obj_type) 
        return TaggedItem.objects\
                .select_related('tag')\
                .filter(content_type=content_type, 
                        object_id=obj_id
                )
    # this method will return all tags for a given object type and object id by querying the TaggedItem model. here we are using select_related to fetch the related tag in the same query to avoid N+1 query problem.

# Create your models here.
class Tag(models.Model):
    lable = models.CharField(max_length=255)

    def __str__(self):
        return self.lable

class TaggedItem(models.Model):
    objects = TaggedItemManager() # assigning the custom manager to the model
    # what tag applies to what object
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    # poor way of doing this
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    # generic way of doing this
    # this needs 3 fields 1. content_type, 2. object_id, 3. content_object
    # need Type (product, video, article), id of the object (1, 2, 3) adn content object (actual object)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()  # content_type, object_id