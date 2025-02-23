from django.shortcuts import *
from django.http import HttpResponse
from django.contrib import messages
from administrator.models import *
from seller.models import *
from customer.models import *

def home(request):
    if "userid" in request.session:
       user = User.objects.get(id=request.session.get("userid"))
       if user.rights == 'seller':
           if not user.approved:
              return redirect('logout')
           return redirect('seller_dashboard')
       elif user.rights == 'admin':
           return redirect('admin_dashboard')
    category = Category.objects.all()
    products = Product.objects.all().prefetch_related('images', 'prices')   
    return render(request, "customer/home.html", {
        'categories': category,
        'products': products,
    })

def item(request, product_id):
    revPerm = False
    if "userid" in request.session:
       user = User.objects.get(id=request.session.get("userid"))
       item = Order.objects.filter(buyer=user,product=product_id)
       if item:
           revPerm = True

    reviews = Review.objects.filter(product=product_id)
    product = Product.objects.prefetch_related('images', 'prices').get(id=product_id)
    return render(request, "customer/item.html", {
        'product': product,
        'revPerm':revPerm,
        'reviews':reviews,
    })

def logout_view(request):
    if "userid" in request.session:
        del request.session["userid"]  
    return redirect("home") 