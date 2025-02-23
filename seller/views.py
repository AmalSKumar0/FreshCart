from django.shortcuts import render, redirect
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


def seller_dashboard(request):
    user = User.objects.get(id=request.session.get("userid"))
    allOrders = Order.objects.filter(seller=user)
    additional_charges = 0
    unique_buyers = set()
    for order in allOrders:
        if order.buyer.id not in unique_buyers:
            unique_buyers.add(order.buyer.id)
            buyer_orders = Order.objects.filter(
                seller=user,
                buyer=order.buyer,
            )
            total_cost = sum(item.price * item.quantity for item in buyer_orders)
            if total_cost < 500:
                additional_charges += 50

    start_date = timezone.now().replace(day=1)
    end_date = start_date + timedelta(days=31)

    monthly_earnings = Order.objects.filter(
        seller=user,
        date_time__range=(start_date, end_date)
    ).aggregate(total_earnings=Sum(F('price') * F('quantity')))['total_earnings'] or 0

    total_earnings = Order.objects.filter(seller=user).aggregate(
        total_earnings=Sum(F('price') * F('quantity'))
    )['total_earnings'] or 0

    total_earnings += additional_charges
    total_expence = 0
    for order in allOrders:
         total_expence += (order.price * Decimal("0.8")) + (order.quantity * Decimal("5"))

    total_profit = total_earnings - total_expence
      
    orders = Order.objects.filter(
        seller=user,
        date_time__range=(start_date, end_date)
    )

    additional_charges = 0
    unique_buyers = set()
    for order in orders:
        if order.buyer.id not in unique_buyers:
            unique_buyers.add(order.buyer.id)
            buyer_orders = Order.objects.filter(
                seller=user,
                buyer=order.buyer,
                date_time__range=(start_date, end_date)
            )
            total_cost = sum(item.price * item.quantity for item in buyer_orders)
            if total_cost < 500:
                additional_charges += 50

    monthly_earnings += additional_charges

    daily_sales = []
    for day in range(15):
        date = timezone.now() - timedelta(days=day)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        day_orders = Order.objects.filter(
            seller=user,
            date_time__range=(day_start, day_end)
        )

        day_income = 0
        day_expense = 0
        unique_buyers = set()
        for order in day_orders:
            if order.buyer.id not in unique_buyers:
                unique_buyers.add(order.buyer.id)
                buyer_orders = Order.objects.filter(
                    seller=user,
                    buyer=order.buyer,
                    date_time__range=(day_start, day_end)
                )
                total_cost = sum(item.price for item in buyer_orders)
                if total_cost < 500:
                    day_income += 50

            day_income += order.price
            day_expense += (order.price * Decimal("0.8")) + (order.quantity * Decimal("5"))

        daily_sales.append({
            'day': day_start.date(),
            'income': day_income,
            'expense': day_expense
        })

    daily_sales = sorted(daily_sales, key=lambda x: x['day'])

    total_orders = Order.objects.filter(seller=user).count()
    pending_orders = Order.objects.filter(seller=user, status='processing').count()
    cancelled_orders = Order.objects.filter(seller=user, status='cancelled').count()
    completed_orders = Order.objects.filter(seller=user, status='delivered').count()

    PendingPer = (pending_orders / total_orders) * 100 if total_orders else 0
    cancelledPer = (cancelled_orders / total_orders) * 100 if total_orders else 0
    completedPer = (completed_orders / total_orders) * 100 if total_orders else 0

    two_days_ago = timezone.now() - timedelta(days=2)
    two_day_sales = Order.objects.filter(
        seller=user,
        date_time__gte=two_days_ago
    ).count()

    noofcustomers = Order.objects.filter(seller=user).values('buyer').distinct().count()
    two_day_customers = Order.objects.filter(
        seller=user,
        date_time__gte=two_days_ago
    ).values('buyer').distinct().count()

    return render(request, 'seller/dashboard.html', {
        'monthly_earnings': monthly_earnings,
        'total_orders': total_orders,
        'noofcustomers': noofcustomers,

        'pending_orders': pending_orders, 'PendingPer': int(PendingPer),
        'cancelled_orders': cancelled_orders, 'cancelledPer': int(cancelledPer),
        'completed_orders': completed_orders, 'completedPer': int(completedPer),
        'daily_sales': daily_sales,
        'total_profit': int(total_profit),'profitPer': int(((total_profit/total_earnings)if total_profit else 0)*100),
        'total_earnings': total_earnings,'eraningPer': 100,
        'total_expence': int(total_expence),'expencePer':int(((total_expence/total_earnings)if total_expence else 0)*100),
    })


def allProducts(request):
    vendor = User.objects.get(id=request.session.get("userid"))
    products = Product.objects.filter(vendor=vendor).prefetch_related('images', 'prices')
    
    return render(request, 'seller/allProducts.html', {
        'products': products
    })

def remove_product(request, product_id):
    Product.objects.get(id=product_id).delete()
    messages.success(request, "Product removed")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

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
            approved=False, 
            rights='seller', 
            photo=photo
        )
        return redirect('login')
    return render(request, 'seller/signup.html')

def notapproved(request):
    return render(request,'seller/notapproved.html')

def allOrders(request):
    user = User.objects.get(id=request.session.get("userid"))
    orders = Order.objects.filter(seller=user)
    return render(request,'seller/orders.html',{'orders':orders})

def singleOrder(request, order_id):
    user = User.objects.get(id=request.session.get("userid"))
    order = Order.objects.get(id=order_id)
    total = order.quantity * order.price
    other_orders = Order.objects.annotate(
        minute_time=TruncMinute('date_time')  # Truncate to minute level
    ).filter(
        minute_time=TruncMinute(order.date_time),  # Match the minute
        buyer__id=order.buyer.id,
        seller = user
    )
    

    if request.method == "POST":
       status = request.POST.get('status')
       if status:
          other_orders.update(status=status)
          return redirect('singleOrder',order_id)
          
    order_total = 0
    shipping = 0

    for item in other_orders:
        item.subTotal = item.quantity*item.price
        order_total += (item.quantity*item.price) 
   
    if order_total<500:
        shipping = 50

    subTotal = order_total + shipping

    return render(request,'seller/orderOverview.html',{'order':order,'total':total,'other_orders':other_orders,'order_total':order_total,'shipping':shipping,'subTotal':subTotal})

def viewCustomers(request):
    user = User.objects.get(id=request.session.get("userid"))
    orders = Order.objects.filter(seller=user)
    customers = []
    for order in orders:
        customer_orders = Order.objects.filter(buyer=order.buyer, seller=user)
        total_cost = sum(item.quantity * item.price for item in customer_orders)
        if not any(c['customer'] == order.buyer for c in customers):
            customers.append({
            'customer': order.buyer,
            'date_time': order.date_time,
            'total_cost': total_cost,
            })
    return render(request,'seller/myCustomers.html',{'customers':customers})

def allreviews(request):
    return render(request,'seller/allreviews.html')