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
    for product in products:
        rating = 0
        count = 0
        reviews = Review.objects.filter(product = product.id)
        for review in reviews:
            count+=1
            rating+=review.rating
        if rating > 0:
            rating = rating/count
        product.rating = rating
        product.rcount = count 
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

    rating = 0
    count = 0
    reviews = Review.objects.filter(product = product.id)
    class RatingObject:
        def __init__(self):
            self.star1 = 0
            self.star2 = 0
            self.star3 = 0
            self.star4 = 0
            self.star5 = 0

    rating_obj = RatingObject()
    for review in reviews:
        if review.rating == 1: 
            rating_obj.star1+=1
        elif review.rating == 2: 
            rating_obj.star2+=1
        elif review.rating == 3: 
            rating_obj.star3+=1
        elif review.rating == 4: 
            rating_obj.star4+=1
        else: 
            rating_obj.star5+=1
        count+=1
        rating+=review.rating
    if rating > 0:
        rating = rating/count
    product.rating = rating
    product.rcount = count

    if rating_obj.star1 > 0: 
            rating_obj.star1 = (rating_obj.star1/count)*100
    if rating_obj.star2 > 0: 
            rating_obj.star2 = (rating_obj.star2/count)*100
    if rating_obj.star3 > 0: 
            rating_obj.star3 = (rating_obj.star3/count)*100
    if rating_obj.star4 > 0: 
            rating_obj.star4 = (rating_obj.star4/count)*100
    if rating_obj.star5 > 0: 
            rating_obj.star5 = (rating_obj.star5/count)*100


    return render(request, "customer/item.html", {
        'product': product,
        'revPerm':revPerm,
        'reviews':reviews,
        'rating_obj':rating_obj,
    })

def logout_view(request):
    if "userid" in request.session:
        del request.session["userid"]  
    return redirect("home") 