from django.contrib import admin
from django.urls import path
from .views import *
from seller.views import *
from administrator.views import *

urlpatterns = [
    path('add_to_cart', add_to_cart, name="add_to_cart"),
    path('remove_cart/<int:cart_id>', remove_cart, name="remove_cart"),
    path('remove_like/<int:like_id>',remove_like,name="remove_like"),
    path('update_cart', update_cart, name="update_cart"),
    path('user_cart', user_cart, name="user_cart"),
    path('shop_home', shop_home, name="shop_home"),
    path('wishlist', wishlist, name="wishlist"),
    path('add_to_wishlist', add_to_wishlist, name="add_to_wishlist"),
    path('checkout/',checkout,name="checkout"),
    path('add_address/',add_address,name="add_address"),
    path('order/',order,name="order"),
    path('customer_reg/',customer_reg,name="customer_reg"),

    # ------address------
    path('setdefaultAddress/',setdefaultAddress,name='setdefaultAddress'),
    path('deleteAddress/',deleteAddress,name="deleteAddress"),
    # ------profile------
    path('settings/',acc_settings,name="acc_settings"),
    path('address-change',address_settings,name="acc_address"),
    path('your_orders/',acc_orders,name="acc_orders"),
    path('notifications/',notifications,name="notifications"),
    path('delete_order/<int:order_id>', delete_order, name="delete_order"),
    path('cancel_order/<int:order_id>', cancel_order, name="cancel_order"),
    path('post_review/',post_review,name="post_review"),
    path('delete_review/<int:rid>', delete_review, name="delete_review"),
]