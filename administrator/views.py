from django.shortcuts import render, redirect, get_object_or_404
from administrator.models import *
from .models import *  
from delivery.models import * 
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
                        return redirect('notapproved')
                    return redirect('seller_dashboard')
                elif user.rights == "delivery":
                    if not user.approved:
                        return redirect('agentnotapproved')
                    return redirect('agent_dashboard')
                else: 
                    return redirect('home')
            else:
                messages.error(request, "Invalid Password.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'administrator/signin.html')


def admin_dashboard(request):
    all_carts = Cart.objects.all()
    customers = User.objects.filter(rights="customer")
    sellers = User.objects.filter(rights="seller",approved=True)
    

    cart_count = all_carts.count()
    customer_count = customers.count()
    seller_count = sellers.count()

    start_date = timezone.now().replace(day=1)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month - timedelta(days=next_month.day)

    new_customers = customers.filter(created_at__range=(start_date, end_date)).count()
    new_products = Product.objects.all().count()

    period = request.GET.get('period', '15_days')
    daily_stats = []
    days_to_skip = 1
    week_counter = 0

    if period == '15_days':
        days_range = 15
    elif period == '4_weeks':
        days_range = 35
        days_to_skip = 7
        week_counter = 5
    elif period == 'months':
        days_range = 30 * 7
        days_to_skip = 30
        week_counter = 7
    else:
        days_range = 15  

    for day in range(0, days_range, days_to_skip):
        if period != '15_days' and day == 0:
            continue
        week_counter -= 1
        date = timezone.now() - timedelta(days=day)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=days_to_skip)

        cart_count_day = Cart.objects.filter(date_time__range=(day_start, day_end)).count()
        customer_count_day = customers.filter(created_at__range=(day_start, day_end)).count()
        seller_count_day = sellers.filter(created_at__range=(day_start, day_end)).count()

        if period == '15_days':
            label = day_start.date()
        elif period == '4_weeks':
            label = 'Week ' + str(week_counter)
        elif period == 'months':
            label = 'Month ' + str(week_counter)
        else:
            label = day_start.date()

        daily_stats.append({
            'day': label,
            'order': cart_count_day,
            'customer': customer_count_day,
            'seller': seller_count_day
        })

    daily_stats = sorted(daily_stats, key=lambda x: x['day'])

    # Order Status Counts
    pending_count = Cart.objects.filter(status__in=['processing', 'shipped']).count()
    cancelled_count = Cart.objects.filter(status='cancelled').count()
    shipped_count = Cart.objects.filter(status='shipped').count()
    delivered_count = Cart.objects.filter(status='delivered').count()

    def get_percentage(count):
        return int((count / cart_count) * 100) if cart_count else 0

    two_days_ago = timezone.now() - timedelta(days=2)
    recent_sales = Cart.objects.filter(date_time__gte=two_days_ago).count()

    return render(request, 'administrator/dashboard.html', {
        'current_page': 1,
        'customer': customer_count,
        'cusCount': new_customers,
        'selCount': seller_count,
        'selweek': new_products,
        'total_orders': cart_count,
        'two_day_sales': recent_sales,
        'pending_orders': pending_count, 'PendingPer': get_percentage(pending_count),
        'cancelled_orders': cancelled_count, 'cancelledPer': get_percentage(cancelled_count),
        'completed_orders': delivered_count, 'completedPer': get_percentage(delivered_count),
        'shipped_orders': shipped_count, 'shippedPer': get_percentage(shipped_count),
        'daily_sales': daily_stats,
        'period': period
    })



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
    return render(request, 'administrator/addCategories.html',{
        'current_page':3,
    })

def category_list(request):

    categories  = Category.objects.all()
    print(categories)

    for cat in categories:
        cat.count = Product.objects.filter(category=cat).count()

    paginator = Paginator(categories, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'administrator/categories.html', {'categories': page_obj,'page_obj':page_obj, 'current_page':3,})

def customer_list(request):
    customers = User.objects.filter(rights="customer")
    customer_data = []

    for customer in customers:
        customer_carts = Cart.objects.filter(buyer=customer)
        cart_ids = customer_carts.values_list('id', flat=True)
        
        cart_products = CartProduct.objects.filter(cart_id__in=cart_ids)

        total_cost = sum(item.quantity * item.price for item in cart_products)

        latest_cart = customer_carts.order_by('-date_time').first()
        latest_date = latest_cart.date_time if latest_cart else None

        customer_data.append({
            'customer': customer,
            'date_time': latest_date,
            'total_cost': total_cost,
        })

    paginator = Paginator(customer_data, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'administrator/customers.html', {
        'customers': page_obj,
        'page_obj': page_obj,
        'current_page': 6
    })



def seller_list(request):
    sellers = User.objects.filter(rights="seller", approved=True)

    for seller in sellers:
        seller.orderCount = Cart.objects.filter(seller=seller).count()
        seller.compCount = Cart.objects.filter(seller=seller, status='delivered').count()

    paginator = Paginator(sellers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'administrator/sellers.html', {
        'sellers': page_obj,
        'page_obj': page_obj,
        'current_page': 5
    })

def agent_list(request):
    agent = User.objects.filter(rights="delivery",approved = True)
    paginator = Paginator(agent, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'administrator/delivery.html', {'agents': page_obj,'page_obj':page_obj, 'current_page':8,})

def newAgent(request):
    agent = User.objects.filter(rights="delivery",approved = False)
    for ag in agent:
        data = DeliveryAgent.objects.filter(agent=ag).first()
        if data:
            ag.address = data.address
            ag.pancard_no = data.pancard_no
            ag.bank_account_number = data.bank_account_number
            ag.license = data.license

    paginator = Paginator(agent, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    return render(request,'administrator/newDelivery.html',{'agents':page_obj,'page_obj':page_obj,'current_page':8,})


def order_list(request):
    orders = Cart.objects.all()
    for order in orders:
        order.items = order.cart_products.all()
        order.count = order.items.count()
        order.subTotal = sum(item.quantity * item.price for item in order.items)
        order.total = order.subTotal + order.delivery_charge

    paginator = Paginator(orders, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'administrator/orders.html', {'orders': page_obj,'page_obj':page_obj, 'current_page':4,})

def products_list(request):
    products = Product.objects.all()
    paginator = Paginator(products, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    return render(request, 'administrator/products.html', {'products': page_obj,'page_obj':page_obj, 'current_page':2,})

def review_list(request):
    reviews = Review.objects.all()
    paginator = Paginator(reviews, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    return render(request, 'administrator/reviews.html', {'reviews': page_obj,'page_obj':page_obj, 'current_page':7,})

def orderSingle(request, order_id):
    cart = get_object_or_404(Cart, id=order_id)
    cart_products = CartProduct.objects.filter(cart=cart)
    total = sum(p.quantity * p.price for p in cart_products) + cart.delivery_charge


    if request.method == "POST":
        status = request.POST.get('status')
        if status:
            cart.status=status
            cart.save()
            return redirect('orderSingle', order_id=order_id)
        
    for cp in cart_products:
        cp.subtotal = cp.price * cp.quantity

    return render(request, 'administrator/orderSingle.html', {
        'current_page': 4,
        'order': cart,
        'total': total,
        'other_orders': cart_products,
        'order_total': total,
        'shipping': cart.delivery_charge,
        'subTotal': total,
    })


def newSellers(request):
    sellers = User.objects.filter(rights="seller",approved = False)
    for sel in sellers:
        data = SellerDetails.objects.filter(seller=sel).first()
        if data:
            sel.GSTIN = data.GSTIN
            sel.PancardNo = data.PancardNo
            sel.bank_account_number = data.bank_account_number
            sel.ifsc_code = data.ifsc_code

    paginator = Paginator(sellers, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    return render(request,'administrator/newSellers.html',{'sellers':page_obj,'page_obj':page_obj,'current_page':5,})

def delete_user(request,user_id):
    User.objects.get(id=user_id).delete()
    messages.success(request, "User removed")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def delete_cat(request,id):
    Category.objects.get(id=id).delete()
    messages.success(request, "Category removed")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def approveSeller(request,user_id):
    user = User.objects.get(id=user_id)
    user.approved = True
    user.save()
    messages.success(request, "User Approved")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def approveAll(request):
    user = User.objects.filter(approved = False,rights="seller")
    for use in user:
        use.approved = True
        use.save()
    messages.success(request, "all Users approved")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def approveAllAgent(request):
    user = User.objects.filter(approved = False,rights="delivery")
    for use in user:
        use.approved = True
        use.save()
    messages.success(request, "all Users approved")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def accountSettings(request):
    return render(request,'administrator/settings.html')

def deliveryEdit(request, user_id):
    user = User.objects.get(id=user_id)
    details = DeliveryAgent.objects.filter(agent=user).first()
    if request.method == "POST":
        name = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        address = request.POST.get('address')
        pan = request.POST.get('pan')
        bank_account_number = request.POST.get('bank')
        license = request.POST.get('dl')
        
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Email Exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        
        if User.objects.filter(phone_no=phone_no).exclude(id=user.id).exists():
            messages.error(request, "Phone no Exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        details.address = address
        details.pancard_no = pan
        details.bank_account_number = bank_account_number
        details.license = license
        details.save()

        user.name = name
        user.email = email
        user.phone_no = phone_no
        user.save()
        messages.success(request, "Updated")
        return redirect('agent_list')
    return render(request, 'administrator/deliveryEdit.html',{'user':user,'details': details,'current_page':8})

def editCustomer(request,user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        name = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Email Exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        
        if User.objects.filter(phone_no=phone_no).exclude(id=user.id).exists():
            messages.error(request, "Phone no Exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        user.name = name
        user.email = email
        user.phone_no = phone_no
        user.save()
        messages.success(request, "Updated")
        return redirect('customer_list')
    return render(request, 'administrator/customerEdit.html',{'user':user,'current_page':6})

def editVendor(request, user_id):
    user = User.objects.get(id=user_id)
    details = SellerDetails.objects.filter(seller=user).first()
    if request.method == "POST":
        name = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        address = request.POST.get('address')
        pan = request.POST.get('pan')
        bank_account_number = request.POST.get('bank')
        code = request.POST.get('code')
        
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Email Exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        
        if User.objects.filter(phone_no=phone_no).exclude(id=user.id).exists():
            messages.error(request, "Phone no Exist")
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        details.Address = address
        details.PancardNo = pan
        details.bank_account_number = bank_account_number
        details.ifsc_code = code
        details.save()

        user.name = name
        user.email = email
        user.phone_no = phone_no
        user.save()
        messages.success(request, "Updated")
        return redirect('seller_list')
    return render(request, 'administrator/vendorEdit.html',{'user':user,'details': details,'current_page':5})

def productEdit(request,pid):
    product = Product.objects.get(id=pid)
    prices = product.prices.all()
    if request.method == "POST":
        category = Category.objects.get(id=request.POST["category"]) 
        vendor = User.objects.get(id=request.session.get("userid"))
        if Product.objects.filter(product_code=request.POST["product_code"]).exclude(id=pid).exists():
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

        return redirect("products_list") 
    cat = Category.objects.all() 
    return render(request, 'administrator/editProduct.html', {'categories': cat,'product': product,'prices': prices,'current_page':4})

