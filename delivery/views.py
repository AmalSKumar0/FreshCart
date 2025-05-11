from django.shortcuts import render, redirect, get_object_or_404
from administrator.models import *
from seller.models import *   
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

def register_delivery(request):
    if request.method == "POST":
        vendor = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        password = request.POST.get('password')
        photo = request.FILES.get('photo')

        license = request.POST.get('dl')
        pan = request.POST.get('pan')
        bank_account_number = request.POST.get('bank')
        address = request.POST.get('address')

        if User.objects.filter(email=email).exists():
            return render(request, 'delivery/signup.html', {'error': 'Email already registered'})

        
        if User.objects.filter(phone_no=phone_no).exists():
            return render(request, 'delivery/signup.html', {'error': 'Phone no already registered'})

        user = User.objects.create(
            name=vendor,
            email=email,
            phone_no=phone_no,
            password=password, 
            approved=False, 
            rights='delivery', 
            photo=photo
        )

        DeliveryAgent.objects.create(
            agent=user,
            address=address,
            pancard_no=pan,
            bank_account_number=bank_account_number,
            license=license
        )

        return redirect('login')
    return render(request, 'delivery/signup.html')


def agentnotapproved(request):
    return render(request,'seller/notapproved.html')

def agent_dashboard(request):
    if "userid" in request.session:
        user = User.objects.get(id=request.session.get("userid"))

    cart = Cart.objects.filter(delivery_user=user)

    total_orders = cart.count()
    total_delivered = cart.filter(status='delivered').count()
    day7 = cart.filter(date_time__gte=timezone.now() - timedelta(days=7)).count()

    money = total_delivered * 50
    money7 = day7 * 50

    allAv = Cart.objects.filter(
        delivery_user = None,
        status = 'shipped',
    ).count()
       
    return render(request, 'delivery/agent_dashboard.html', {'user': user,'current_page':1,'total_orders': total_orders, 'total_delivered': total_delivered, 'money': money, 'day7': day7, 'money7': money7, 'allAv': allAv})


def newAvailableDeliveries(request):
    user = None
    if "userid" in request.session:
        user = User.objects.get(id=request.session.get("userid"))
    
    address = DeliveryAgent.objects.filter(agent=user).first().address

    if 'q' in request.GET:
        address = request.GET.get('q')
 
    data = Cart.objects.filter(
        seller__seller_details__Address__icontains=address,
        status='shipped',
        delivery_user__isnull=True
    )

    for op in data:
        products = CartProduct.objects.filter(cart = op).count()
        op.count = products

    paginator = Paginator(data, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'delivery/findalldelivery.html',{'dataobj':page_obj,'address':address,'page_obj':page_obj,'current_page':2})

def Mydeliveries(request):
    user = None
    if "userid" in request.session:
        user = User.objects.get(id=request.session.get("userid"))

    data = Cart.objects.filter(
        delivery_user=user,
        status='shipped'
    )

    for op in data:
        products = CartProduct.objects.filter(cart = op).count()
        op.address = op.seller.seller_details.Address
        op.count = products

    paginator = Paginator(data, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'delivery/allDeliveries.html',{'dataobj':page_obj,'page_obj':page_obj,'current_page':3})

def history(request):
    user = None
    if "userid" in request.session:
        user = User.objects.get(id=request.session.get("userid"))

    data = Cart.objects.filter(
        delivery_user=user,
        status='delivered'
    )

    for op in data:
        products = CartProduct.objects.filter(cart = op).count()
        op.address = op.seller.seller_details.Address
        op.count = products

    paginator = Paginator(data, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'delivery/history.html',{'dataobj':page_obj,'page_obj':page_obj,'current_page':4})

def allocate(request, cart_id):
    user = None
    if "userid" in request.session:
        user = User.objects.get(id=request.session.get("userid"))
    Cart.objects.filter(id=cart_id).update(delivery_user=user)
    sendOTP(request, cart_id)
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def sendOTP(request, cart_id):
    cart = Cart.objects.get(id=cart_id)
    otp = cart.generate_otp()
    Message.objects.create(
        user=cart.buyer,
        message_type='otp',
        subject='Delivery Confirmation OTP',
        content=f'Your OTP for confirming the delivery of your order(#ORID{cart_id}) is {otp}. Please use this to verify your delivery.',
        expires_at=timezone.now() + timedelta(hours=2)
    )
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def closerLook(request,cart_id):
    user = User.objects.get(id=request.session.get("userid"))
    order = get_object_or_404(Cart, id=cart_id, delivery_user=user)

    if 'otp' in request.GET:
        if order.delivery_otp == request.GET.get('otp'):
            order.status = "delivered"
            order.save()
            messages.success(request,'Delivery successful')
            return redirect('Mydeliveries')
        else:
            messages.error(request,'invalid otp')


    if request.method == "POST":
        status = request.POST.get('status')
        if status:
            order.status=status
            order.save()
            return redirect('singleOrder', order_id=order.id )

    order_total = 0

    items = order.cart_products.select_related('product')
    for cart_product in items:
        cart_product.subTotal = cart_product.quantity * cart_product.price
        order_total += cart_product.subTotal

    shipping = order.delivery_charge
    grand_total = order_total + shipping

    return render(request, 'delivery/closerlook.html', {
        'order': order,
        'current_page':3,
        'other_orders': items,
        'order_total': order_total,
        'shipping': shipping,
        'subTotal': grand_total
    })

def delSettings(request):
    user = None
    if "userid" in request.session:
        user = User.objects.get(id=request.session.get("userid"))
    details = DeliveryAgent.objects.filter(agent=user).first()
    if request.method == "POST":
        name = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        password = request.POST.get('password')
        photo = request.FILES.get('photo')
        address = request.POST.get('address')
        pan = request.POST.get('pan')
        bank_account_number = request.POST.get('bank')
        license = request.POST.get('dl')
        
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return render(request, 'delivery/accountSettings.html', {'error': 'Email already registered'})

        
        if User.objects.filter(phone_no=phone_no).exclude(id=user.id).exists():
            return render(request, 'delivery/accountSettings.html', {'error': 'Phone no already registered'})
        details.address = address
        details.pancard_no = pan
        details.bank_account_number = bank_account_number
        details.license = license
        details.save()

        user.name = name
        user.email = email
        user.phone_no = phone_no
        user.password = password
        user.photo = photo
        user.save()

    return render(request, 'delivery/accountSettings.html',{'details': details})

def cannotBeDelivered(request, cart_id):
    user = None
    if "userid" in request.session:
        user = User.objects.get(id=request.session.get("userid"))
    order = get_object_or_404(Cart, id=cart_id, delivery_user=user)
    order.status = "cancelled"
    order.save()
    messages.success(request,'Order cancelled')
    return redirect('Mydeliveries')

