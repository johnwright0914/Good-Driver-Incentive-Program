from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .fields import SeparatedTextField
#from django.contrib.postgres.fields import ArrayField
    

# sponsor model all user profiles need to be linked to one
class Sponsor(models.Model):
    name = models.CharField(default="Sponsor", max_length=255)

    def __str__(self):
        return self.name

# Model for individual Promotions
class Promotion(models.Model):
    # profile = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(default="#PROMOTION_NAME", max_length=255)
    description = models.CharField(default="#PROMO_DESCRIPTION", max_length=255)
    multiplier = models.FloatField(default=1.0)

    def __str__(self):
        return self.name
    
class Promotion_l(models.Model):
    list = models.ManyToManyField(Promotion, blank=True)

# Extends auth_user model 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.IntegerField(null=True)    
    points = models.IntegerField(default=0, blank=True)
    promotions = models.ManyToManyField(Promotion)
    SponsorID = models.ForeignKey(Sponsor, on_delete=models.PROTECT, default=1, blank=True)
    
    # using postgres array field with mysql is causing issues 
    #known_ips = ArrayField(models.GenericIPAddressField())
    known_ips = models.CharField(max_length=100, blank=True)
    ebay_username = models.CharField(default='', max_length=50, blank=True, null=True)
    refresh_token = models.CharField(default='', max_length=100,  blank=True, null=True)
    
# creates Profile instance with creation of User instance
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
# saves Profile instance with save of User instance
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Application(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    sponsor = models.ForeignKey(Sponsor, on_delete=models.PROTECT, blank=True)
    approved = models.BooleanField(default=False)

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

# model for Products
class Product(models.Model):
    #category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # note: IDs should be auto generated by default
    name = models.CharField(default="Product", max_length=255)
    description = models.TextField(default="[Product Description]", blank=True, null=True)
    price_dollars = models.FloatField(default=0.0)
    inventory = models.IntegerField(default = 0)
    # price points are stored for now in the product db
    # we can change this later on but it is needed right now since
    # Catalog and Products are not linked at the moment
    price_points = models.IntegerField(default=0)
    # possible models.ImageField() to look into
    #image = models.ImageField(upload_to='products/')
    image = models.ImageField(default="", blank=True, null=True, max_length=255)
    categories = models.CharField(default="", blank=True, null=True, max_length=255)
    tags = SeparatedTextField(token=',',blank=True) 

    def __str__(self):
        return self.name

# model to hold a collection of Products by id
class Product_catalog(models.Model):
    ProductIDs = models.ManyToManyField(Product, blank=True, null=True)

# model for a catalouge of products also hold point conversion rate
class Catalog(models.Model):
    product_catalog = models.OneToOneField(Product_catalog, on_delete=models.CASCADE)
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    conversion_rate = models.FloatField(default=0.01)

    def __str__(self):
        return "Catalog"

class Order(models.Model):
    order_time = models.DateTimeField()
    point_total = models.IntegerField(default=0)
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)

# model to hold products for an order 
class Order_Details(models.Model):
    OrderID = models.ForeignKey(Order, primary_key=True, on_delete=models.CASCADE, unique=False)
    products = models.ManyToManyField(Product)
    quantity = models.IntegerField(default=0)


