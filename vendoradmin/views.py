from django.shortcuts import render, redirect
from core.models import CartOrder, Product, Category, CartOrderItems, productReview
from userauths.models import Profile
from django.db.models import Sum
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from userauths.models import User
from vendoradmin.forms import AddProductForm
from vendoradmin.decorators import adminRequired
import datetime


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
    allProducts = Category.objects.all().order_by("-id")
    allCategories = Category.objects.all()

    context = {
        "allProducts":allProducts,
        "allCategories":allCategories,
    }

    return render(request, "vendoradmin/products.html", context)

@adminRequired
def addProducts(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()

            # Many to many field below
            form.save_m2m()
            return redirect("vendoradmin:dashboard")
        else:
            form = AddProductForm()

        context = {
            "form":form
        }

        return render(request, "venoradmin/add-product.html", context)
    

@adminRequired
def editProduct(request, pid):
    product = Product.objects.get(pid=pid)
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()

            # Many to many field below
            form.save_m2m()
            return redirect("vendoradmin:edit_product", product.pid)
        else:
            form = AddProductForm(instance=product)

        context = {
            "form":form,
            "product":product,
        }

        return render(request, "venoradmin/edit-product.html", context)
    

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
def orderDetail(request,pid):
    orders = CartOrder.objects.all()
    orderItems = CartOrderItems.objects.filter(orders=orders)
    context = {
        "orders":orders,
        "orderItems":orderItems,
    }

    return render(request,"vendoradmin/order_detailhtml", context)


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
    reviews = productReview.objects.all

    context = {
        "reviews":reviews,
    }

    return render(request, "", context)

@adminRequired
def settings(request):
    # Go in userauths.models Profile table
    profile = Profile.objects.get(user = request.user)

    if request.method == "POST":
        image = request.FILES.get("image")
        full_name = request.FILES.get("full_name")
        phone = request.FILES.get("phone")
        bio = request.FILES.get("bio")
        address = request.FILES.get("address")
        coutnry = request.FILES.get("country")

        if image != None:
            profile.image = image
        
        profile.full_name = full_name
        profile.phone = phone
        profile.bio = bio
        profile.address = address
        profile.country = coutnry

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("vendoradmin:settings")

    context = {
        "profile":profile
    }

    return render(request, "vendoradmin/settings.html", context)

@adminRequired
def changePassword(request):
    user = request.user

    if request.method == "POST":
        oldPassword = request.POST.get("oldPassword")
        newPassword = request.POST.get("newPassword")
        confirmNewPassword = request.POST.get("confirmNewPassword")

        if confirmNewPassword != newPassword:
            messages.error(request, "Passowrd didn't match!")
            return redirect("vendoradmin:changePassword")
        
        if check_password(oldPassword, user.password):
            user.setPassword(newPassword)
            user.save()
            messages.success(request, "Changed Successfully!")
            return redirect("vendoradmin:changePassword")
        else:
            messages.error(request, "Old Password is Incorrect")
            return redirect("vendoradmin:changePassword")
    return render(request, "vendoradmin/change_password.html")
