from django.db import models
from django.utils.timezone import now
from administrator.models import *
from seller.models import *
import random


class Cart(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_buyer",
                              limit_choices_to={'rights': 'customer'})  
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_seller",
                               limit_choices_to={'rights': 'seller'}) 
    delivery_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name="orders_as_delivery_user",
                                      limit_choices_to={'rights': 'delivery'}) 
    location = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
    ]
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cod')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    date_time = models.DateTimeField(default=now)
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def generate_otp(self):
        otp = str(random.randint(100000, 999999))
        self.delivery_otp = otp
        self.save()
        return otp

    def __str__(self):
        return f"Cart {self.id} - Buyer: {self.buyer.username} - Delivery User: {self.delivery_user.username if self.delivery_user else 'Unassigned'}"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="in_carts")
    quantity = models.PositiveIntegerField()
    weight = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # (quantity * unit_price)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"


class liked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user.name} liked {self.product.name}"
    
class UserCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart")
    quantity = models.PositiveIntegerField(default=0)
    date_time = models.DateTimeField(default=now)
    weight = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    def __str__(self):
        return f"{self.user.name}'s cart"