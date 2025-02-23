from django.contrib import admin
from django.urls import path
from .views import *
from seller.views import *
from administrator.views import *
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('seller_dashboard/',seller_dashboard,name="seller_dashboard"),
    path('add_product/',add_product,name="add_product"),
    path('allProducts/',allProducts,name="allProducts"),
    path('remove_product/<int:product_id>/',remove_product,name="remove_product"),
    path('register_vendor/',register_vendor,name="register_vendor"),
    path('all_orders/',allOrders,name="allOrders"),
    path('singleOrder/<int:order_id>/',singleOrder,name="singleOrder"),
    path('viewCustomers/',viewCustomers,name="viewCustomers"),
    path('allreviews/',allreviews,name="allreviews"),
    path('notapproved/',notapproved,name="notapproved")
]