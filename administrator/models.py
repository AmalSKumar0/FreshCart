from django.db import models
from django.utils.timezone import now

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  
    approved = models.BooleanField(default=True)
    phone_no = models.CharField(max_length=15, unique=True)
    rights = models.CharField(
        max_length=50,
        choices=[('admin', 'Admin'), ('seller', 'Seller'), ('customer', 'Customer')],
        default='customer'
    )
    created_at = models.DateTimeField(default=now, editable=False)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)  

    def __str__(self):
        return self.name

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")  
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    product_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Weight(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="weights")
    value = models.FloatField() 

    def __str__(self):
        return f"{self.value} kg - {self.category.name}"

class Message(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="messages")  
    message = models.TextField() 
    timestamp = models.DateTimeField(default=now) 

    def __str__(self):
        return f"Message from {self.user.name} at {self.timestamp}"
