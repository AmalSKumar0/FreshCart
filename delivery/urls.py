from django.contrib import admin
from django.urls import path
from .views import *
from seller.views import *
from administrator.views import *
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('agent-registration/',register_delivery,name="register_delivery"),
    path('agent-not-approved/',agentnotapproved,name="agentnotapproved"),
    path('agent-dashboard/',agent_dashboard,name="agent_dashboard"),
    path('new-agents/',newAgent,name="newAgent"),
    path('findalldelivery/',newAvailableDeliveries,name="findalldelivery"),
    path('Mydeliveries/',Mydeliveries,name="Mydeliveries"),
    path('history/',history,name="history"),
    path('assign/<int:cart_id>',allocate,name="allocate"),
    path('closerlook/<int:cart_id>',closerLook,name="closerlook"),
    path('sendOTP/<int:cart_id>',sendOTP,name="sendOTP"),
    path('cannotBeDelivered/<int:cart_id>',cannotBeDelivered,name="cannotBeDelivered"),
    path('delSettings/',delSettings,name="delSettings"),
] 
