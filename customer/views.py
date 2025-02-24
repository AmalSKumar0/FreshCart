from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from administrator.models import *
from seller.models import *
from customer.models import *
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404

def customer_reg(request):
    if request.method == "POST":
        name = request.POST.get('first_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        password = request.POST.get('password')
        photo = request.FILES.get('photo')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'customer/signup.html')
        
        if User.objects.filter(phone_no=phone_no).exists():
            messages.error(request, "Phone no already registered")
            return render(request, 'customer/signup.html')
            
        user = User.objects.create(
            name=name,
            email=email,
            phone_no=phone_no,
            password=password,  
            rights='customer', 
            photo=photo
        )
        return redirect('login')
    return render(request, 'customer/signup.html')

def shop_home(request):
    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.filter(availability=True).prefetch_related('images', 'prices')

    category = request.GET.get('category')
    if category:
        products = products.filter(category=Category.objects.get(id=category))
        category=Category.objects.get(id=category)

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

    count = len(products)

    paginator = Paginator(products, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    

    return render(request, 'customer/shop-wide.html', {
        'categories': categories,
        'products': page_obj,
        'query': query,
        'count': count,
        'page_obj': page_obj,
        'category' : category,
    })


def add_to_cart(request):
    user = User.objects.get(id=request.session.get("userid"))
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        quantity = int(request.POST.get('quantity'))
        price = float(request.POST.get('price'))
        Weight = request.POST.get('weight')
        
        cart_item, created = Cart.objects.get_or_create(user=user, product=product, price=price, weight=Weight)
        cart_item.quantity += quantity
        product.stock -= quantity
        product.save()
        cart_item.save()
        
        messages.success(request, "Product added to cart.")
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    messages.error(request, "Product not added to cart.")
    return HttpResponse("Invalid request.")


def remove_cart(request, cart_id):
    if request.method == "POST":
       item_deleted = Cart.objects.get(id=cart_id)
       item_deleted.product.stock += item_deleted.quantity
       item_deleted.delete()
       messages.success(request, "Item removed successfully")
       return JsonResponse({"success": True, "message": "Item removed successfully"})
    messages.error(request, "Item not removed")
    return JsonResponse({"error": "Invalid request"}, status=400)

def update_cart(request):
    user = User.objects.get(id=request.session.get("userid"))
    if request.method == "POST":
        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            edited=int(request.POST.get("quantity_" + str(item.id), 0))
            product = Product.objects.get(id=item.product.id)
            product.stock+=item.quantity-edited
            product.save()
            item.quantity = edited
            item.save()
        messages.success(request, "Cart updated")
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    messages.error(request, "failed")
    return HttpResponse("Invalid request.")

def user_cart(request):
    user = User.objects.get(id=request.session.get("userid"))
    cart_items = Cart.objects.filter(user=user)
    cart_total = sum([item.price * item.quantity for item in cart_items])
    shipping = 0
    if cart_total < 500:
        shipping = 50
    shop = 500 - cart_total
    subtotal = cart_total + shipping
    count = len(cart_items)
    for item in cart_items:
        item.max_quantity = item.quantity + item.product.stock
    return render(request, 'customer/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'shipping': shipping,
        'subtotal': subtotal,
        'shop': shop,
    })

def wishlist(request):
    user = User.objects.get(id=request.session.get("userid"))
    wishlist_items = liked.objects.filter(user=user)
    count = len(wishlist_items)
    return render(request, 'customer/wishlist.html', {
        'wishlist_items': wishlist_items,
        'count': count,
    })

def remove_like(request, like_id):
    user = User.objects.get(id=request.session.get("userid"))
    liked_item = liked.objects.get(user=user, id=like_id)
    liked_item.delete()
    messages.success(request, "Successfully removed")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def add_to_wishlist(request):
    user = User.objects.get(id=request.session.get("userid"))
    if not user:
        return redirect('login')
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    liked.objects.get_or_create(user=user, product=product)
    messages.success(request, "Product added to wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def checkout(request):
    user = User.objects.get(id=request.session.get("userid"))
    try:
        PrimaryAddresses = Address.objects.get(user=user, is_primary=True)
    except Address.DoesNotExist:
        PrimaryAddresses = None

    addresses = Address.objects.filter(user=user, is_primary=False)
    cart_items = Cart.objects.filter(user=user)
    cart_total = sum([item.price * item.quantity for item in cart_items])
    shipping = 0
    if cart_total < 500:
        shipping = 50
    shop = 500 - cart_total
    subtotal = cart_total + shipping
    count = len(cart_items)
    for item in cart_items:
        item.max_quantity = item.quantity + item.product.stock
    return render(request, 'customer/checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'shipping': shipping,
        'subtotal': subtotal,
        'count': count,
        'shop': shop,
        'addresses': addresses,
        'PrimaryAddresses': PrimaryAddresses,
    })


def add_address(request):
    user = User.objects.get(id=request.session.get("userid"))
    if request.method=="POST":
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code') 
        if request.POST.get('is_primary') == 'True':
            obj = Address.objects.filter(user=user,is_primary=True).first()
            if obj:
                obj.is_primary = False
                obj.save()
        Address.objects.create(
            user = user,
            street = street,
            city = city,
            state = state,
            postal_code = postal_code,
            is_primary = request.POST.get('is_primary') == 'True',
        )
    messages.success(request, "Address added")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def order(request):
    user = User.objects.get(id=request.session.get("userid"))
    if request.method=="POST":
        payment = request.POST.get('flexRadioDefault')
        address = Address.objects.get(id=request.POST.get('address'))
        status = 'processing'

        

        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            Order.objects.create(
                buyer = user,
                seller = item.product.vendor,
                product = item.product,
                quantity = item.quantity,
                weight = item.weight,
                price = item.price,
                location = address,
                payment_method = payment,
                status = status,
            )
            item.delete()
    return redirect('home')


# ------------------- profile -------------------

def acc_settings(request):
    return render(request,'customer/profile/settings.html')


def address_settings(request):
    user = User.objects.get(id=request.session.get("userid"))
    try:
        PrimaryAddresses = Address.objects.get(user=user, is_primary=True)
    except Address.DoesNotExist:
        PrimaryAddresses = None

    addresses = Address.objects.filter(user=user, is_primary=False)

    return render(request,'customer/profile/Address.html',{
        'addresses': addresses,
        'PrimaryAddresses': PrimaryAddresses,
    })

def setdefaultAddress(request):
    user = get_object_or_404(User, id=request.session.get("userid"))
    addressId = request.GET.get('address')

    if not addressId:
        messages.error(request, "Invalid address ID.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    current_primary = Address.objects.filter(user=user, is_primary=True).first()
    if current_primary:
        current_primary.is_primary = False
        current_primary.save()

    new_primary = get_object_or_404(Address, id=addressId, user=user)
    new_primary.is_primary = True
    new_primary.save()

    messages.success(request, "Default address updated successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def deleteAddress(request):
    addressId = request.GET.get('address')
    address = Address.objects.get(id=addressId)
    address.delete()
    messages.success(request, "Deleted")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def acc_orders(request):
    user = User.objects.get(id=request.session.get("userid"))
    ordered_items = Order.objects.filter(buyer=user)
    from django.core.paginator import Paginator
    paginator = Paginator(ordered_items, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'customer/profile/account_orders.html'
                  ,{
                      'ordered_items' : page_obj,'page_obj':page_obj,'count':ordered_items.count()
                  })

def notifications(request):
    return render(request,'customer/profile/notifications.html')


def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cancelled' 
    order.save()  
    messages.success(request, "Order cancelled")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete() 
    messages.success(request, "Order Deleted")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def post_review(request):
    user = User.objects.get(
        id=request.session.get("userid")
        )
    if request.method=="POST":
        Review.objects.create(
            user=user,
            product = Product.objects.get(id = request.POST.get('pid')),
            rating = request.POST.get('star'),
            review = request.POST.get('review')
        )
        messages.success(request, "review Posted")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def delete_review(request,rid):
    Review.objects.get(id=rid).delete()
    messages.success(request, "review Deleted")
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def allOrders(request):
    user = User.objects.get(id=request.session.get("userid"))
    orders = Order.objects.filter(seller=user)
    return render(request,'seller/orders.html',{'orders':orders})

