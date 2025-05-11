from django.db import models
from django.utils.timezone import now
from django.utils import timezone

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  
    approved = models.BooleanField(default=True)
    phone_no = models.CharField(max_length=15, unique=True)
    rights = models.CharField(
        max_length=50,
        choices=[('admin', 'Admin'), ('seller', 'Seller'), ('customer', 'Customer'), ('delivery', 'Delivery')],
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


class Message(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('notification', 'Notification'),
        ('otp', 'OTP'),
        ('alert', 'Alert'),
        ('promo', 'Promotional'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)  # useful for OTPs

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.message_type.upper()} to {self.user.username}"

    class Meta:
        ordering = ['-sent_at']