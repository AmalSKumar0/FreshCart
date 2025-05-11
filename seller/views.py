from django.shortcuts import render, redirect, get_object_or_404
from administrator.models import *
from .models import *   
from customer.models import *
from administrator.models import *
from django.db.models import Sum
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.db.models.functions import TruncMinute
from django.core.paginator import Paginator



def seller_dashboard(request):
    user = User.objects.get(id=request.session.get("userid"))
    allOrders = Cart.objects.filter(seller=user)

    start_date = timezone.now().replace(day=1)
    end_date = start_date + timedelta(days=31)

    current_month_orders = Cart.objects.filter(seller=user, date_time__range=(start_date, end_date))
    monthly_earnings = 0
    for order in current_month_orders:
        monthly_earnings += order.delivery_charge
        for cp in order.cart_products.all():
            monthly_earnings += cp.price * cp.quantity
        if order.status == 'delivered':
            monthly_earnings = monthly_earnings - 50
    

    # Daily/Weekly/Monthly Stat
    period = request.GET.get('period', '15_days')
    if period == '15_days':
        days_range, days_to_skip, week = 15, 1, 0
    elif period == '4_weeks':
        days_range, days_to_skip, week = 35, 7, 5
    elif period == 'months':
        days_range, days_to_skip, week = 30 * 7, 30, 7
    else:
        days_range, days_to_skip, week = 15, 1, 0

    daily_stat = []

    for day in range(0, days_range, days_to_skip):
        if period != '15_days' and day == 0:
            continue
        week -= 1
        day_start = (timezone.now() - timedelta(days=day)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=days_to_skip)

        day_orders = Cart.objects.filter(seller=user, date_time__range=(day_start, day_end))

        day_income = 0
        day_expense = 0
        for order in day_orders:
            order.items = order.cart_products.all()
            for item in order.items:
                day_income  += item.quantity * item.price
            day_income += order.delivery_charge
            if order.status == 'delivered':
                day_expense += 50
        
        if period == '15_days':
            day_label = day_start.date()
        elif period == '4_weeks':
            day_label = 'Week ' + str(week)
        elif period == 'months':
            day_label = 'Month ' + str(week)
        else:
            day_label = day_start.date()

        daily_stat.append({
            'day': day_label,
            'income': day_income,
            'expense': day_expense
        })

    daily_stat = sorted(daily_stat, key=lambda x: x['day'])

    total_orders = allOrders.count()
    pending_orders = allOrders.filter(status__in=['processing', 'shipped']).count()
    cancelled_orders = allOrders.filter(status='cancelled').count()
    completed_orders = allOrders.filter(status='delivered').count()

    PendingPer = (pending_orders / total_orders) * 100 if total_orders else 0
    cancelledPer = (cancelled_orders / total_orders) * 100 if total_orders else 0
    completedPer = (completed_orders / total_orders) * 100 if total_orders else 0

    two_days_ago = timezone.now() - timedelta(days=2)
    two_day_sales = Cart.objects.filter(seller=user, date_time__gte=two_days_ago).count()
    noofcustomers = Cart.objects.filter(seller=user).values('buyer').distinct().count()
    two_day_customers = Cart.objects.filter(seller=user, date_time__gte=two_days_ago).values('buyer').distinct().count()

    return render(request, 'seller/dashboard.html', {
        'monthly_earnings': monthly_earnings,
        'period': period,
        'total_orders': total_orders,
        'noofcustomers': noofcustomers,
        'pending_orders': pending_orders, 'PendingPer': int(PendingPer),
        'cancelled_orders': cancelled_orders, 'cancelledPer': int(cancelledPer),
        'completed_orders': completed_orders, 'completedPer': int(completedPer),
        'daily_sales': daily_stat,
                })


def allProducts(request):
    vendor = User.objects.get(id=request.session.get("userid"))
    products = Product.objects.filter(vendor=vendor).prefetch_related('images', 'prices')
    paginator = Paginator(products, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    

    return render(request, 'seller/allProducts.html', {
        'products': page_obj,'page_obj':page_obj
    })

def remove_product(request, product_id):
    Product.objects.get(id=product_id).delete()
    messages.success(request, "Product removed")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def add_product(request):
    if request.method == "POST":
        category = Category.objects.get(id=request.POST["category"]) 
        vendor = User.objects.get(id=request.session.get("userid"))
        if Product.objects.filter(product_code = request.POST["product_code"]).exists():
            messages.success(request, "Product code exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        product = Product.objects.create(
            name=request.POST["pname"],
            description=request.POST.get("description", ""),
            category=category,
            stock=int(request.POST["stock"]),
            product_code=request.POST["product_code"],
            availability="available" in request.POST, 
            brand=request.POST.get("brand", ""),
            is_veg=request.POST.get("inlineRadioOptions") == "veg",
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

        gst = request.POST.get('gstin')
        pan = request.POST.get('pan')
        bank_account_number = request.POST.get('bank')
        ifsc_code = request.POST.get('ifsc')
        address = request.POST.get('Address')

        if User.objects.filter(email=email).exists():
            return render(request, 'seller/signup.html', {'error': 'Email already registered'})

        if SellerDetails.objects.filter(GSTIN=gst).exists():
            return render(request, 'seller/signup.html', {'error': 'GSTIN already registered'})
        
        if User.objects.filter(phone_no=phone_no).exists():
            return render(request, 'seller/signup.html', {'error': 'Phone no already registered'})

        user = User.objects.create(
            name=vendor,
            email=email,
            phone_no=phone_no,
            password=password, 
            approved=False, 
            rights='seller', 
            photo=photo
        )
        SellerDetails.objects.create(
            seller=user,
            GSTIN=gst,
            PancardNo=pan,
            bank_account_number=bank_account_number,
            ifsc_code=ifsc_code,
            Address = address
        )

        return redirect('login')
    return render(request, 'seller/signup.html')

def notapproved(request):
    return render(request,'seller/notapproved.html')

# View: All Orders
def allOrders(request):
    user = User.objects.get(id=request.session.get("userid"))
    orders = Cart.objects.filter(seller=user).order_by('-date_time')
    for order in orders:
        order.items = order.cart_products.all()
        order.count = order.items.count()
        order.subTotal = sum(item.quantity * item.price for item in order.items)
        order.total = order.subTotal + order.delivery_charge

    paginator = Paginator(orders, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'seller/orders.html', {'orders': page_obj, 'page_obj': page_obj})



def singleOrder(request, order_id):
    user = User.objects.get(id=request.session.get("userid"))
    order = get_object_or_404(Cart, id=order_id, seller=user)

    if request.method == "POST":
        status = request.POST.get('status')
        if status:
            if status == 'shipped' and order.status != 'shipped':
                order.delivery_user = None
            order.status=status
            order.save()
            return redirect('singleOrder', order_id=order.id)

    order_total = 0

    items = order.cart_products.select_related('product')
    for cart_product in items:
        cart_product.subTotal = cart_product.quantity * cart_product.price
        order_total += cart_product.subTotal

    shipping = order.delivery_charge
    grand_total = order_total + shipping

    return render(request, 'seller/orderOverview.html', {
        'order': order,
        'other_orders': items,
        'order_total': order_total,
        'shipping': shipping,
        'subTotal': grand_total
    })


# View: Customers List
def viewCustomers(request):
    user = User.objects.get(id=request.session.get("userid"))
    orders = Cart.objects.filter(seller=user).order_by('-date_time')
    
    customers = []
    seen = set()
    for order in orders:
        buyer = order.buyer
        if buyer.id in seen:
            continue
        buyer_orders = Cart.objects.filter(buyer=buyer, seller=user)
        total_cost = sum(cp.quantity * cp.price for o in buyer_orders for cp in o.cart_products.all())
        customers.append({
            'customer': buyer,
            'date_time': order.date_time,
            'total_cost': total_cost,
        })
        seen.add(buyer.id)

    paginator = Paginator(customers, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
   
    return render(request, 'seller/myCustomers.html', {'customers': page_obj, 'page_obj': page_obj})

# View: All Reviews
def allreviews(request):
    user = User.objects.get(id=request.session.get("userid"))
    reviews = Review.objects.filter(product__vendor=user).order_by('-id')
    paginator = Paginator(reviews, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
   
    return render(request, 'seller/allreviews.html', {'reviews': page_obj, 'page_obj': page_obj})

# View: Seller Settings Page
def selSettings(request):
    return render(request, 'seller/settings.html')

def edit_product(request,product_id):
    product = Product.objects.get(id=product_id)
    prices = product.prices.all()
    if request.method == "POST":
        category = Category.objects.get(id=request.POST["category"]) 
        vendor = User.objects.get(id=request.session.get("userid"))
        if Product.objects.filter(product_code=request.POST["product_code"]).exclude(id=product_id).exists():
            messages.success(request, "Product code exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        product.name = request.POST["pname"]
        product.description = request.POST.get("description", "")
        product.category = category
        product.stock = int(request.POST["stock"])
        product.product_code = request.POST["product_code"]
        product.availability = "available" in request.POST
        product.brand = request.POST.get("brand", "")
        product.is_veg = request.POST.get("inlineRadioOptions") == "veg"
        product.vendor = vendor
        product.save()

        weights_prices = [
            (request.POST["w1"], request.POST["p1"]),
            (request.POST["w2"], request.POST["p2"]),
            (request.POST["w3"], request.POST["p3"]),
        ]

        Price.objects.filter(product=product).delete()

        for weight_id, price in weights_prices:
            Price.objects.create(
            product=product,
            weight=weight_id,
            price=price,
            )

        return redirect("allProducts") 
    cat = Category.objects.all() 
    return render(request, 'seller/editProduct.html', {'categories': cat,'product': product,'prices': prices})

