from django.shortcuts import render, redirect
from core.models import CartOrder, Product, Category, CartOrderItems, productReview, Vendor
from userauths.models import Profile
from django.db.models import Sum
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from userauths.models import User
from vendoradmin.forms import AddProductForm
from vendoradmin.decorators import adminRequired
import datetime
from django.contrib.auth.hashers import check_password
'''
It may be getting confusing now, but here's a note for you (the reader) to understand what's going on here.
Inside of the core directory and userauths directory you'll find yourself looking at similar python file names such as, 
    views.py, models.py, urls.py, admin.py, and etc. 

It's important for us to separate these functionalities into 
'''


'''
What do vendors need? Take some time to think about it and write it below:
    1) Revenue - vendorsProducts
    2) Total Amount of Orders - vendorsProducts
    3) All their products - vendorsProducts
    4) All their categories
'''

@adminRequired
def vendorDashboard(request):
    revenue = CartOrder.objects.aaggregate(price=Sum("price"))
    totalOrdersCount = CartOrder.objects.all()
    allProducts = Category.objects.all()
    allCategories = Category.objects.all()
    newCustomers = User.objects.all().order_by("-id")
    latestOrders = CartOrder.objects.all()

    currentMonth = datetime.datetime.now().month
    monthlyRevenue = CartOrder.objects.filter(order_date__month=currentMonth).aggregate(price=Sum("price"))

    context = {
        "revenue":revenue,
        "totalOrdersCount":totalOrdersCount,
        "allProducts":allProducts,
        "allCategories":allCategories,
        "newCustomers":newCustomers, 
        "latestOrders":latestOrders, 
        "monthlyRevenue":monthlyRevenue,
    }

    return render(request, "vendoradmin/dashboard.html", context)

@adminRequired
def vendorsProducts(request):
    all_products = Product.objects.all().order_by("-id")
    allCategories = Category.objects.all()

    context = {
        "all_products": all_products,
        "allCategories": allCategories,
    }

    return render(request, "vendoradmin/products.html", context)

@adminRequired
def addProducts(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            
            # Set vendor if available
            try:
                vendor = Vendor.objects.get(user=request.user)
                new_form.vendor = vendor
            except Vendor.DoesNotExist:
                pass
                
            new_form.save()

            # Many to many field below
            form.save_m2m()
            messages.success(request, "Product added successfully!")
            return redirect("vendoradmin:products")
    else:
        form = AddProductForm()

    context = {
        "form": form
    }

    return render(request, "vendoradmin/add-product.html", context)
    

@adminRequired
def editProduct(request, pid):
    product = Product.objects.get(pid=pid)
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            
            # Toggle the product status
            if product.product_status == "published":
                new_form.product_status = "draft"
                messages.success(request, "Product unpublished and saved.")
            else:
                new_form.product_status = "published"
                messages.success(request, "Product published successfully!")
            
            # Set vendor if available
            try:
                vendor = Vendor.objects.get(user=request.user)
                new_form.vendor = vendor
            except Vendor.DoesNotExist:
                pass
                
            new_form.save()

            # Many to many field below
            form.save_m2m()
            return redirect("vendoradmin:products")
    else:
        form = AddProductForm(instance=product)

    context = {
        "form": form,
        "product": product,
    }

    return render(request, "vendoradmin/edit-product.html", context)
    

@adminRequired
def deleteProduct(request, pid):
    product = Product.objets.get(pid=pid)
    product.delete()
    return redirect("vendoradmin:products")

@adminRequired
def orders(request):
    orders = CartOrder.objects.all()
    context = {
        "orders":orders,
    }

    return render(request,"vendoradmin/orders.html", context)

@adminRequired
def orderDetail(request, id):
    order = CartOrder.objects.get(id=id)
    order_items = CartOrderItems.objects.filter(order=order)
    context = {
        "order": order,
        "order_items": order_items,
    }

    return render(request, "vendoradmin/order-detail.html", context)


@csrf_exempt
def changeOrderStatus(request, oid):
    order = CartOrder.objects.get(oid=oid)
    if request.method == "POST":
        status = request.POST.get("status")
        order.product_status = status
        order.save()
        messages.success(request,f" Order status changed to {status}")
    
    return redirect("vendoradmin:order_detail", order.id)

@adminRequired
def shopPage(request):
    products = Product.objects.filter(user=request.user)
    revenue = CartOrder.objects.aggregate(price=Sum("price"))
    totalSales = CartOrderItems.objects.filter(order__paid_status=True).aggregate(qty=Sum("qty"))
    context = {
        "products":products,
        "revenue":revenue,
        "totalSales":totalSales,
    }

    return render(request, "vendoradmin/shop_page.html", context)

@adminRequired
def reviews(request):
    reviews = productReview.objects.all()

    context = {
        "reviews":reviews,
    }

    return render(request, "vendoradmin/reviews.html", context)

@adminRequired
def settings(request):
    # Get user profile
    profile = Profile.objects.get(user=request.user)

    # Try to get vendor associated with this user
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        vendor = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        
        # Handle profile form submission
        if form_type == "profile":
            image = request.FILES.get("image")
            full_name = request.POST.get("full_name")
            phone = request.POST.get("phone")
            bio = request.POST.get("bio")
            address = request.POST.get("address")
            country = request.POST.get("country")

            if image:
                profile.image = image
            
            profile.full_name = full_name
            profile.phone = phone
            profile.bio = bio
            profile.address = address
            profile.country = country

            profile.save()
            messages.success(request, "Profile updated successfully!")
            
        # Handle vendor form submission
        elif form_type == "vendor" and vendor:
            vendor_title = request.POST.get("vendor_title")
            description = request.POST.get("description")
            vendor_address = request.POST.get("vendor_address")
            vendor_mobile = request.POST.get("vendor_mobile")
            vendor_profile_image = request.FILES.get("vendor_profile_image")
            vendor_banner = request.FILES.get("vendor_banner")

            if vendor_title:
                vendor.vendor_title = vendor_title
            
            if description:
                vendor.description = description
                
            if vendor_address:
                vendor.vendor_address = vendor_address
                
            if vendor_mobile:
                vendor.vendor_mobile = vendor_mobile
            
            if vendor_profile_image:
                vendor.vendor_profile_image = vendor_profile_image
                
            if vendor_banner:
                vendor.vendor_banner = vendor_banner
            
            vendor.save()
            messages.success(request, "Vendor information updated successfully!")
        
        return redirect("vendoradmin:settings")

    context = {
        "profile": profile,
        "vendor": vendor
    }

    return render(request, "vendoradmin/settings.html", context)

@adminRequired
def changePassword(request):
    user = request.user

    if request.method == "POST":
        oldPassword = request.POST.get("old_password")
        newPassword = request.POST.get("new_password")
        confirmNewPassword = request.POST.get("confirm_new_password")

        if confirmNewPassword != newPassword:
            messages.error(request, "Password didn't match!")
            return redirect("vendoradmin:change_password")
        
        if check_password(oldPassword, user.password):
            user.set_password(newPassword)
            user.save()
            messages.success(request, "Changed Successfully!")
            return redirect("vendoradmin:change_password")
        else:
            messages.error(request, "Old Password is Incorrect")
            return redirect("vendoradmin:change_password")
    return render(request, "vendoradmin/change_password.html")
