from django.shortcuts import *
from django.http import HttpResponse
from django.contrib import messages
from administrator.models import *
from seller.models import *
from customer.models import *


def home(request):
    category = Category.objects.all()
    products = Product.objects.all().prefetch_related('images', 'prices')   
    return render(request, "customer/home.html", {
        'categories': category,
        'products': products,
    })

def item(request, product_id):
    product = Product.objects.prefetch_related('images', 'prices').get(id=product_id)
    return render(request, "customer/item.html", {
        'product': product,
    })

def logout_view(request):
    if "userid" in request.session:
        del request.session["userid"]  
    return redirect("home") 