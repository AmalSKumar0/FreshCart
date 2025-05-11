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
    path('login/',user_login,name="login"),
    path('item/<int:product_id>/',item,name="item"),
    path('logout/',logout_view,name="logout"),

    path('customer/', include('customer.urls')),
    path('administrator/', include('administrator.urls')),
    path('seller/',include('seller.urls')),
    path('delivery/',include('delivery.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
