from django.db import models
from django.utils.timezone import now
from administrator.models import *
from seller.models import *

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_buyer",
                              limit_choices_to={'rights': 'customer'})  
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_seller",
                               limit_choices_to={'rights': 'seller'}) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField()
    weight = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Stores total price (quantity * unit price)
    location = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cod')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    date_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"Order {self.id} - {self.product.name} by {self.buyer.name}"

class liked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user.name} liked {self.product.name}"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart")
    quantity = models.PositiveIntegerField(default=0)
    date_time = models.DateTimeField(default=now)
    weight = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    def __str__(self):
        return f"{self.user.name}'s cart"