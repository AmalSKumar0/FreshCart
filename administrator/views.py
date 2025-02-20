from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import *
from seller.models import *
from customer.models import *
from django.contrib import messages
from django.contrib.auth.hashers import check_password

def editAccount(request):
    user = User.objects.get(id=request.session.get("userid"))
    if request.method == "POST":
        name = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        user.name = name
        user.email = email
        user.phone_no = phone_no
        user.save()
    messages.success(request, "Account updated successfully")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
       
def resetPassword(request):
    user = User.objects.get(id=request.session.get("userid"))
    if request.method == "POST":
        password = request.POST.get('pass')
        conpass = request.POST.get('conpass')
        if password == conpass:
           user.password = password
           user.save()
           messages.success(request, "Password Changed.")
        else:
           messages.error(request, "Password does not match.")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if user.password == password:
                request.session['userid'] = user.id
                if user.rights == "admin":
                    return redirect('admin_dashboard')
                elif user.rights == "seller":
                    if not user.approved:
                        messages.error(request, "Your account is not approved yet.")
                        return redirect('login',{'error': "Your account is not approved yet."})
                    return redirect('seller_dashboard')
                else: 
                    return redirect('home')
            else:
                messages.error(request, "Invalid Password.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'administrator/signin.html')


def admin_dashboard(request):
    return render(request, 'administrator/dashboard.html')

def add_category(request):
    if request.method == "POST":
        catPic = request.FILES.get('catPic')
        cname = request.POST.get('cname')
        if cname:  
            Category.objects.create(
                name=cname,
                icon=catPic,
                product_status=True
            )
            messages.success(request, "Category added")
            return redirect('category_list')
        else:
            messages.error(request, "Category name cannot be empty.")
            return redirect('add_category')
    return render(request, 'administrator/addCategories.html')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'administrator/categories.html', {'categories': categories})

def customer_list(request):
    customers = User.objects.filter(rights="customer")
    return render(request, 'administrator/customers.html', {'customers': customers})

def seller_list(request):
    sellers = User.objects.filter(rights="seller")
    return render(request, 'administrator/sellers.html', {'sellers': sellers})

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'administrator/orders.html', {'orders': orders})

def products_list(request):
    products = Product.objects.all()
    return render(request, 'administrator/products.html', {'products': products})

def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'administrator/reviews.html', {'reviews': reviews})
