from django.shortcuts import render, redirect
from administrator.models import *
from .models import *   
from customer.models import *
from administrator.models import *

def seller_dashboard(request):
    return render(request, 'seller/dashboard.html')


def allProducts(request):
    vendor = User.objects.get(id=request.session.get("userid"))
    products = Product.objects.filter(vendor=vendor).prefetch_related('images', 'prices')
    
    return render(request, 'seller/allProducts.html', {
        'products': products
    })

def remove_product(request, product_id):
    Product.objects.get(id=product_id).delete()
    return redirect('allProducts')

def add_product(request):
    if request.method == "POST":
        category = Category.objects.get(id=request.POST["category"]) 
        vendor = User.objects.get(id=request.session.get("userid"))
        product = Product.objects.create(
            name=request.POST["pname"],
            description=request.POST.get("description", ""),
            category=category,
            stock=int(request.POST["stock"]),
            product_code=request.POST["product_code"],
            availability="available" in request.POST, 
            brand=request.POST.get("brand", ""),
            is_veg=request.POST.get("ingredients") == "veg",
            vendor=vendor,
        )

        weights_prices = [
            (request.POST["w1"], request.POST["p1"]),
            (request.POST["w2"], request.POST["p2"]),
            (request.POST["w3"], request.POST["p3"]),
        ]

        for weight_id, price in weights_prices:
            Price.objects.create(
            product=product,
            weight=weight_id,
            price=price,
            )
        
        images = [
            request.FILES.get("image1"),
            request.FILES.get("image2"),
            request.FILES.get("image3"),
            request.FILES.get("image4"),
        ]
        for image in images:
            ProductImage.objects.create(
                product=product,
                image=image,
            )

        return redirect("allProducts") 
    cat = Category.objects.all() 
    return render(request, 'seller/addProducts.html', {'categories': cat})

def register_vendor(request):
    if request.method == "POST":
        vendor = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        password = request.POST.get('password')
        photo = request.FILES.get('photo')

        if User.objects.filter(email=email).exists():
            return render(request, 'seller/signup.html', {'error': 'Email already registered'})
        
        if User.objects.filter(phone_no=phone_no).exists():
            return render(request, 'seller/signup.html', {'error': 'Phone no already registered'})

        user = User.objects.create(
            name=vendor,
            email=email,
            phone_no=phone_no,
            password=password,  
            rights='seller', 
            photo=photo
        )
        return redirect('login')
    return render(request, 'seller/signup.html')


