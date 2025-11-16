from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # best practice is to create a custom user model even if you don't need to customize it immediately.
    # because once you start a project, changing the user model later is complicated. 
    # So it's better to have a custom user model from the beginning even if its just an empty class with pass.
    # otherwise, in middle of the project, changing the user model can lead to issues with existing migrations and data.
    # have to drop the database and recreate it which is not ideal in production.

    # pass

    # You can add additional fields here if needed or override existing ones from AbstractUser
    email = models.EmailField(unique=True)

