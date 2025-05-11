from django.contrib import admin
from django.urls import path
from .views import *
from seller.views import *
from administrator.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_dashboard/', admin_dashboard, name="admin_dashboard"),
    path('add_category/', add_category, name="add_category"),
    path('category_list/', category_list, name="category_list"),
    path('customer_list/', customer_list, name="customer_list"),
    path('seller_list/', seller_list, name="seller_list"),
    path('order_list/', order_list, name="order_list"),
    path('review_list/', review_list, name="review_list"),
    path('products_list/', products_list, name="products_list"),
    path('editAccount/',editAccount,name="editAccount"),
    path('resetPassword/',resetPassword,name="resetPassword"),
    path('orderSingle/<int:order_id>/',orderSingle,name="orderSingle"),
    path('newSellers/',newSellers,name="newSellers"),
    path('delete_user/<int:user_id>/',delete_user,name="delete_user"),
    path('approveSeller/<int:user_id>/',approveSeller,name="approveSeller"),
    path('approveAll/',approveAll,name="approveAll"),
    path('approveAllAgent/',approveAllAgent,name="approveAllAgent"),
    path('accountSettings/',accountSettings,name="accountSettings"),
    path('delete_cat/<int:id>', delete_cat, name="delete_cat"),
    path('agent_list/',agent_list,name="agent_list"),
    path('newAgent/',newAgent,name="newAgent"),
    path('delivery-edit/<int:user_id>',deliveryEdit,name="deliveryEdit"),
    path('Customer-edit/<int:user_id>',editCustomer,name="editCustomer"),
    path('Vendor-edit/<int:user_id>',editVendor,name="editVendor"),
    path('productEdit/<int:pid>',productEdit,name="productedit")
]
