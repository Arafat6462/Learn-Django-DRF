from django.db import models
from django.core.validators import MinValueValidator

class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+')

    # This is the default string representation of the object. it is used in the admin site and in the shell.
    # def __str__(self) -> str: 
    #     return super().__str__()

    # Overriding the default string representation of the object to return the title of the collection.
    # This is useful for displaying the collection in the admin site and in the shell.
    def __str__(self) -> str:
        return self.title
    
    # Meta class is used to define metadata for the model. it is used to define ordering, verbose_name, verbose_name_plural, etc.
    # here we are defining the default ordering for the model. it will be used in the admin site and in the shell.
    class Meta:
        ordering = ['title']

    # Meta class vs __str__ method:
    # Meta class is used to define metadata for the model. it is used to define ordering, verbose_name, verbose_name_plural, etc.
    # __str__ method is used to define the string representation of the object. it is used in the admin site and in the shell. 


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    # Product_set will be created automatically in Product model
    # django automatically adds reverse relationship in the related model
    # products = reverse relationship from Product model will be created automatically as 'promotions_set' unless specified otherwise in Product model
    products = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')

class Product(models.Model):
    # in django, primary key is automatically added as id field if not specified otherwise
    # sku = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField() # this will create a slug field which is a short label for something, containing only letters, numbers, underscores or hyphens so that it can be used in URLs
    description = models.TextField()
    unit_price = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(1.00)]
        )
    inventory = models.IntegerField(validators=[MinValueValidator(0)]) # inventory cannot be negative
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True) # blank=True means the field is optional in forms (including admin site, don't show error for blank).

    def __str__(self): # string representation of the object for better readability in admin site and shell. default is super().__str__()
        return self.title
    
    class Meta:
        ordering = ['title'] # default ordering for the model. it will be used in the admin site and in the shell.
        # ordering in Meta class vs ModelAdmin class in admin.py:
        # ordering in Meta class is used to define the default ordering for the model. it will be used in the admin site and in the shell.
        # ordering in ModelAdmin class is used to define the ordering for the model in the admin site only. it will not affect the ordering in the shell.
        

class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True) # null=True means the field can be null in the database, blank=True means the field is optional in forms (including admin site, don't show error for blank).
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    
    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

class OrderItem(models.Model):
    # in Order model, django will automatically create a reverse relationship as orderitem_set unless specified otherwise. this can be changed by adding related_name parameter in ForeignKey
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # django will automatically create a product_id field in the database.
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    # This line creates a one-to-one relationship between your model and the Customer model.
    # Each instance of your model is linked to exactly one Customer.
    # If the Customer is deleted, the related instance is also deleted (CASCADE).
    # The field is also set as the primary key for this model.
    # customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    
    # This line creates a many-to-one relationship (ForeignKey) to the Customer model.
    # Multiple instances of your model can be linked to the same Customer.
    # If the Customer is deleted, all related instances are also deleted (CASCADE).
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
