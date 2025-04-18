from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishListModel, ProductImages, productReview, Address
from django.db.models import Count, Avg
from taggit.models import Tag
from django.template.loader import render_to_string
from core.forms import productReviewForm
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
# added serializers for wishlist inorder for function.js remove wishlist function/feature to work properly
# without the use of serializers will cause tons of issues with django querysets. 
from django.core import serializers
from userauths.models import Profile, ContactUs

# Create your views here.
'''
For the ake of organization, no userauthenitcation view will be used in this section. 
Since I am trying to build a clean final product I want to keep domain separation a thing. 
Therefore, separating the user views not only would help us locate it easily but will help us reuse it for any future projects
'''

def index(request):
    #products = Product.objects.all().order_by("-id")
    products = Product.objects.filter(product_status="published", featured = True)
    context = {
        "products":products
    }    

    return render(request, 'core/index.html', context)  

def product_list_view(request):
    products = Product.objects.filter(product_status="published")

    context = {
        "products":products
    }
    return render(request, 'core/product-list.html', context)


def category_list_view(request):
    categories = Category.objects.all()

    context = {
        "categories":categories
    }
    return render(request, 'core/category-list.html', context)  

def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category":category,
        "products":products,
    }
    return render(request, 'core/category-product-list.html', context)  

def vendor_list_view(request):
    vendors=Vendor.objects.all()
    context = {
        "vendors":vendors,
    }
    return render(request, "core/vendor-list.html", context)

def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    context = {
        "vendor":vendor,
        "products":products,
    }
    return render(request, "core/vendor-detail.html", context)

def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    reviews = productReview.objects.filter(product=product).order_by("-date")

    # average reviews view
    average_rating = productReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Product review form
    review_form = productReviewForm()

    p_image = product.p_images.all()

    make_review = True
    if request.user.is_authenticated:
        user_review_count = productReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False


    context = {
        "p":product,
        'review_form': review_form,
        'make_review':make_review,
        "p_image":p_image,
        "average_rating": average_rating,
        'reviews':reviews, 
        "products":products,
    }
    return render(request, "core/product-detail.html", context)

def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])
    
    context = {
        "products":products,
        "tag":tag,
    }

    return render(request, "core/tag.html", context)

def add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = productReview.objects.create(
        user=user, 
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )
    context = {
        'user': user.username, 
        'review':request.POST['review'],
        'rating':request.POST['rating'],
    }

    average_reviews = productReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
        'bool': True, 
        'context': context,
        'average_reviews':average_reviews,
        }
    )


# when searching, it's going to grab any product that contains the information the user inserted and will output the most latest added products
def search_view(request):
    query = request.GET.get("q")

    products=Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products":products,
        "query":query,
    }
    return render(request, "core/search.html", context)

def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(product_status="published").order_by(".-id").distinct()

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

    if len(categories) > 0:
        products = Product.objects.filter(category_id_in=categories).distinct()

    if len(vendors) > 0:
        products = Product.objects.filter(vendor_id_in=vendors).distinct()

    data = render_to_string("core/async/product-list.html", {"products":products})
    return JsonResponse({"data":data})

def clean_price(price_str):
    # Remove dollar sign and fix multiple decimal points
    price_str = price_str.replace('$', '')
    if price_str.count('.') > 1:
        parts = price_str.split('.')
        price_str = parts[0] + '.' + ''.join(parts[1:])
    return price_str

def add_to_cart(request):
    cart_product = {}
    
    # Clean the price string before storing
    price = clean_price(request.GET['price'])

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': price,
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:

            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data

    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})

def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            price = clean_price(item['price'])
            cart_total_amount += int(item['qty']) * float(price)
        return render(request, "core/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")

def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            price = clean_price(item['price'])
            cart_total_amount += int(item['qty']) * float(price)

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    return JsonResponse({
        "data": context, 
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': "{:.2f}".format(cart_total_amount)
    })


def update_cart(request):
    product_id = str(request.GET["id"])
    product_qty = int(request.GET["qty"])

    if "cart_data_obj" in request.session:
        if product_id in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            cart_data[product_id]["qty"] = product_qty
            request.session["cart_data_obj"] = cart_data

    cart_total_amount = 0
    item_total = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            price = float(clean_price(item['price']))
            cart_total_amount += int(item['qty']) * price
            if p_id == product_id:
                item_total = int(item['qty']) * price
    
    return JsonResponse({
        "status": "success",
        "totalcartitems": len(request.session["cart_data_obj"]),
        "cart_total_amount": "{:.2f}".format(cart_total_amount),
        "item_total": "{:.2f}".format(item_total)
    })

@login_required
def checkout_view(request):
    if 'cart_data_obj' not in request.session:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")

    host = request.get_host()

    paypalDictionary = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount':200,
        'item_name': "Order-Item-Number-2",
        'invoice':"INVOICE-NUMBER-3",
        'currency_code':"USD",
        'notification_url':'http://{}{}'.format(host, reverse("core:paypal-ipn")),
        'return_url':'http://{}{}'.format(host, reverse("core:payment-completed")),
        'cancel_url':'http://{}{}'.format(host, reverse("core:payment-failed"))
    }

    paypal_payment_button = PayPalPaymentsForm(initial=paypalDictionary)

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            price = clean_price(item['price'])
            cart_total_amount = cart_total_amount + int(item['qty']) * float(price)

    try: 
        activeAddress = Address.objects.get(user=request.user, status=True)
    except: 
        messages.warning(request, "You have more than one address activated")
        activeAddress = None

    return render(request, "core/checkout.html", {"cart_data":request.session["cart_data_obj"], "totalcartitems": len(request.session["cart_data_obj"]), 
                                    "cart_total_amount":cart_total_amount, "paypal_payment_button":paypal_payment_button, "activeAddress":activeAddress})

@login_required
def paypalCompletedView(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            cart_total_amount = cart_total_amount + int(item['qty']) * float(item["price"])
    return render(request, 'core/payment-completed.html', {'cart_data':request.session['cart_data_obj'],'totalcartitems':len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})

@login_required
def paypalFailedView(request):
    return render(request, 'core/payment-failed.html')

@login_required
def dashboard(request):
    orderList = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    # Get or create the profile for this user
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Will grab the user's frontend input inside of the dashboard
    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        newAddress = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile
        )
        messages.success(request, "Address saved!")
        return redirect("core:dashboard")
    
    context = {
        "user_profile":user_profile,
        "orderList":orderList,
        "address":address,
    }
    return render(request, 'core/dashboard.html', context)



def orderDetail(request, id):
     orders = CartOrder.objects.get(user=request.user, id=id)
     orderItems = CartOrderItems.objects.filter(order=order)

     context = {
         "orderItems":orderItems,
     }
     return render(request, "core/order-detail.html")

def defaultAddress(request):
    id = request.GET['id']
    
    # Will make all other addresses deactivated (False)
    Address.objects.update(status=False)

    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean":True})


#########   WISHLIST     #########
@login_required
def wishlistView(request):
    wishlist = wishListModel.objects.all()
    context = {
        "w":wishlist
    }
    return render(request, "core/wishlist.html", context)

def addToWishList(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)
    print("product id is:" + product_id)

    context = {}

    wishlist_count = wishListModel.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = wishListModel.objects.create(
            user=request.user,
            product=product,
        )
        context = {
            "bool": True
        }

    return JsonResponse(context)

def removeFromWishlist(request):
    pid = request.GET['id']
    wishlist = wishListModel.objects.filter(user=request.user)
    wishlist_d = wishListModel.objects.get(id=pid)
    delete_product = wishlist_d.delete()
    
    context = {
        "bool":True,
        "w":wishlist
    }
    wishlist_json = serializers.serialize('json', wishlist)
    t = render_to_string('core/async/wishlist-list.html', context)
    return JsonResponse({'data':t,'w':wishlist_json})

def contact(request):
    return render(request, "core/contact.html")


def ajax_contact_form(request):
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    subject = request.POST.get('subject')
    message = request.POST.get('message')

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {
        "bool": True,
        "message": "Message Sent Successfully"
    }

    return JsonResponse({"data":data})
