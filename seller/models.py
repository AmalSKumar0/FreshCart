from django.db import models
from django.utils.timezone import now
from administrator.models import *
from seller.models import *

class SellerDetails(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_details")
    GSTIN = models.CharField(max_length=15, blank=True, null=True)
    PancardNo = models.CharField(max_length=10, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    Address = models.TextField()

    def __str__(self):
        return f"Seller Details for {self.seller.username}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    stock = models.PositiveIntegerField(default=0)
    product_code = models.CharField(max_length=100, unique=True)
    availability = models.BooleanField(default=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    manufacturing_date = models.DateField(blank=True, null=True)
    ingredients_used = models.TextField(blank=True, null=True)
    is_veg = models.BooleanField(default=True)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products",
                               limit_choices_to={'rights': 'seller'})  

    def __str__(self):
        return self.name


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    weight = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"{self.product.name} - {self.weight.value}{self.weight.unit} @ ₹{self.price}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField()
    review = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.name} reviewed {self.product.name} on {self.timestamp}"
