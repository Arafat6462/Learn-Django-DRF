from django.db import models
from django.core.validators import MinValueValidator
from uuid import uuid4

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
    description = models.TextField(null=True, blank=True) # blank=True means the field is optional in forms (including admin site, don't show error for blank).
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
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orderitems') # adding related_name to avoid conflict with promotions field in Product model. now we can access order items of a product using product.orderitems instead of product.orderitem_set.
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

class Cart(models.Model):
    # id = models.AutoField(primary_key=True)  # explicitly defining primary key field, although Django does this automatically if not specified.
    uuid = models.UUIDField(primary_key=True, default=uuid4, unique=True) # using UUIDField as primary key for better security so that cart ids are not predictable. unless specified, Django uses an AutoField which is an integer that auto-increments for primary key. this makes it easy to guess other cart ids and access them illegally. here default=uuid4 generates a random UUID for each new cart. here we are not calling uuid4() function, we are just passing the function itself so that it can be called each time a new cart is created. unless it creates an uuid4 only once at the time of model definition.
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, to_field='uuid', on_delete=models.CASCADE, related_name='ietems') # to_field='uuid' specifies that the ForeignKey should reference the 'uuid' field of the Cart model. related_name='items' allows accessing cart items of a cart using cart.items.
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    # Adding unique_together constraint to ensure that there is only one cart item for a given product in a given cart.
    class Meta:
        unique_together = [['cart', 'product']] # this will ensure that there is only one cart item for a given product in a given cart. it will create a unique constraint on the combination of cart and product fields. example: if a cart already has a cart item for product A, it cannot have another cart item for product A. this is useful to prevent duplicate cart items for the same product in a cart. insted product A quantity should be updated.


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


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews') # related_name allows accessing reviews of a product using product.reviews and CASCADE means if the product is deleted, all its reviews will also be deleted.
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True) # auto_now_add means the field is set to the current date when the object is created. it is not updated when the object is updated.