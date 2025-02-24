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
                else: 
                    return redirect('home')
            else:
                messages.error(request, "Invalid Password.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'administrator/signin.html')


def admin_dashboard(request):
    allOrders = Order.objects.all()
    customers = User.objects.filter(rights="customer")
    seller = User.objects.filter(rights="seller")


    orderCount = allOrders.count()
    cusCount = customers.count()
    sellerCount = seller.count()

    start_date = timezone.now().replace(day=1)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month - timedelta(days=next_month.day)

    weekCountCus = customers.filter(created_at__range=(start_date, end_date)).count()
    two_day_sales = Order.objects.filter(
        date_time__range=(start_date, end_date)
    ).count() 
    weekCountSel = Product.objects.all().count()

    period = request.GET.get('period', '15_days')
    daily_stat = []
    days_to_skip = 1
    week = 0

    if period == '15_days':
        days_range = 15
    elif period == '4_weeks':
        days_range = 35
        days_to_skip = 7
        week = 5
    elif period == 'months':
        days_range = 30 * 7 
        days_to_skip = 30
        week = 7
    else:
        days_range = 15  # Default to 15 days if period is not recognized
 
    
    for day in range(0, days_range, days_to_skip):
        if period != '15_days' and day==0:
            continue
        week -= 1
        date = timezone.now() - timedelta(days=day)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=days_to_skip)

        day_orders = Order.objects.filter(
            date_time__range=(day_start, day_end)
        ).count()
        day_cus = customers.filter(
            created_at__range=(day_start, day_end)
        ).count()
        day_sel = seller.filter(
            created_at__range=(day_start, day_end)
        ).count()

        if period == '15_days':
            day_label = day_start.date()
        
        elif period == '4_weeks':
            day_label = 'Week ' + str(week)
        elif period == 'months':
            day_label = 'Month ' + str(week)
        else:
           day = day_start.date() 
        daily_stat.append({
            'day': day_label,
            'order': day_orders,
            'customer': day_cus,
            'seller': day_sel
        })
    daily_stat = sorted(daily_stat, key=lambda x: x['day'])

    total_orders = Order.objects.all().count()
    pending_orders = Order.objects.filter(status='processing').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    completed_orders = Order.objects.filter(status='delivered').count()

    PendingPer = (pending_orders / total_orders) * 100 if total_orders else 0
    cancelledPer = (cancelled_orders / total_orders) * 100 if total_orders else 0
    completedPer = (completed_orders / total_orders) * 100 if total_orders else 0

    two_days_ago = timezone.now() - timedelta(days=2)
    two_day_sales = Order.objects.filter(
        date_time__gte=two_days_ago
    ).count()


    return render(request, 'administrator/dashboard.html',{
        'current_page':1,
        'customer':cusCount,
        'cusCount':weekCountCus,
        'selCount':sellerCount,
        'selweek':weekCountSel,
        'total_orders': orderCount,
        'two_day_sales': two_day_sales,
        'pending_orders': pending_orders, 'PendingPer': int(PendingPer),
        'cancelled_orders': cancelled_orders, 'cancelledPer': int(cancelledPer),
        'completed_orders': completed_orders, 'completedPer': int(completedPer),
        'daily_sales': daily_stat,
        'period':period
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
    categories = Category.objects.all()
    paginator = Paginator(categories, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'administrator/categories.html', {'categories': page_obj,'page_obj':page_obj, 'current_page':3,})

def customer_list(request):
    customers = User.objects.filter(rights="customer")
    customer_data = []
    for customer in customers:
        customer_orders = Order.objects.filter(buyer=customer)
        total_cost = sum(item.quantity * item.price for item in customer_orders)
        latest_order = customer_orders.order_by('-date_time').first()
        latest_date = latest_order.date_time if latest_order else None
        customer_data.append({
            'customer': customer,
            'date_time': latest_date,
            'total_cost': total_cost,
        })
    paginator = Paginator(customer_data, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'administrator/customers.html', {'customers':page_obj,'page_obj':page_obj , 'current_page': 6})


def orderSingle(request, order_id):
    user = User.objects.get(id=request.session.get("userid"))
    order = Order.objects.get(id=order_id)
    total = order.quantity * order.price
    other_orders = Order.objects.filter(
        date_time__exact=order.date_time,
        seller__exact=user,
        buyer__exact=order.buyer,
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

    return render(request,'administrator/orderOverview.html',{'order':order,'total':total,'other_orders':other_orders,'order_total':order_total,'shipping':shipping,'subTotal':subTotal})


def seller_list(request):
    sellers = User.objects.filter(rights="seller",approved = True)
    for sel in sellers:
        sel.orderCount = Order.objects.filter(seller=sel).count()
        sel.save()
        sel.compCount = Order.objects.filter(seller=sel,status = 'delivered').count()
        sel.save()

    paginator = Paginator(sellers, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'administrator/sellers.html', {'sellers': page_obj,'page_obj':page_obj, 'current_page':5,})

def order_list(request):
    orders = Order.objects.all()
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
    order = Order.objects.get(id=order_id)
    total = order.quantity * order.price

    # Filter other orders with the same buyer and same minute (ignoring seconds)
    other_orders = Order.objects.annotate(
        minute_time=TruncMinute('date_time')  # Truncate to minute level
    ).filter(
        minute_time=TruncMinute(order.date_time),  # Match the minute
        buyer__id=order.buyer.id,
    )
    

    if request.method == "POST":
        status = request.POST.get('status')
        if status:
            other_orders.update(status=status)
            return redirect('orderSingle', order_id=order_id)

    order_total = 0
    shipping = 0
    item_costs = []

    for item in other_orders:
        item.subTotal = item.quantity * item.price
        order_total += item.subTotal
        item_costs.append({
            'item': item,
            'cost': item.subTotal
        })

    if order_total < 500:
        shipping = 50

    subTotal = order_total + shipping

    return render(request, 'administrator/orderSingle.html', {
        'current_page': 4,
        'order': order,
        'total': total,
        'other_orders': other_orders,
        'order_total': order_total,
        'shipping': shipping,
        'subTotal': subTotal,
        'item_costs': item_costs
    })

def newSellers(request):
    sellers = User.objects.filter(rights="seller",approved = False)
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
    user = user.objects.get(id=user_id)
    user.approved = True
    user.save()
    messages.success(request, "User Approved")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def approveAll(request):
    user = User.objects.filter(approved = False)
    for use in user:
        use.approved = True
        use.save()
    messages.success(request, "all Users approved")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def accountSettings(request):
    return render(request,'administrator/settings.html')