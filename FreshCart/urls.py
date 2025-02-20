from django.contrib import admin
from django.urls import path
from .views import *
from seller.views import *
from administrator.views import *
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name="home"),
    path('register_vendor/',register_vendor,name="register_vendor"),
    path('login/',user_login,name="login"),
    path('seller_dashboard/',seller_dashboard,name="seller_dashboard"),
    path('add_product/',add_product,name="add_product"),
    path('allProducts/',allProducts,name="allProducts"),
    path('remove_product/<int:product_id>/',remove_product,name="remove_product"),
    path('item/<int:product_id>/',item,name="item"),
    path('logout/',logout_view,name="logout"),

    path('customer/', include('customer.urls')),
    path('administrator/', include('administrator.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
