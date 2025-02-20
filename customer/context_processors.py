from django.shortcuts import *
from django.http import HttpResponse
from django.contrib import messages
from administrator.models import *
from seller.models import *
from customer.models import *

def common_data(request):
    login = "userid" in request.session
    user = None
    cart_items = []
    cart_total = 0
    cart_count = 0
    like_count = 0
    categories = []
    if login:
        user_id = request.session.get("userid")
        user = User.objects.get(id=user_id)
        cart_items = Cart.objects.filter(user=user)
        cart_total = sum([item.price * item.quantity for item in cart_items])
        like_count = liked.objects.filter(user=user).count()
        cart_count = len(cart_items)
        categories = Category.objects.all()
        for item in cart_items:
           item.max_quantity = item.quantity + item.product.stock

        
    
    return {
        "login": login,
        "user": user,
        "cart_items": cart_items,
        'cart_total':cart_total,
        'cart_count' : cart_count,
        'like_count' : like_count,
        'categories' : categories,
    }