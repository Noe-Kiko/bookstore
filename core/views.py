from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishListModel, ProductImages, productReview, Address, Coupon, becomeVendorModel
from django.db.models import Count, Avg, Min, Max
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

# Not only are we dealing with Paypal for payment but we will be working with stripe
import stripe

# 

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
    
    # Get min and max prices for the price filter
    min_max_price = Product.objects.filter(product_status="published").aggregate(
        price__min=Min('price'),
        price__max=Max('price')
    )
    
    # Set default values if None is returned
    if min_max_price['price__min'] is None:
        min_max_price['price__min'] = 0
    if min_max_price['price__max'] is None:
        min_max_price['price__max'] = 1000

    context = {
        "products": products,
        "min_max_price": min_max_price,
        "categories": Category.objects.all(),
        "vendors": Vendor.objects.all(),
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
    sort_by = request.GET.get("sort", "featured")  # Default sort is featured
    
    products = Product.objects.filter(vendor=vendor, product_status="published")
    
    # Apply sorting based on the sort parameter
    if sort_by == "price_low_to_high":
        products = products.order_by("price")
    elif sort_by == "price_high_to_low":
        products = products.order_by("-price")
    elif sort_by == "release_date":
        products = products.order_by("-date")
    elif sort_by == "avg_rating":
        products = products.order_by("-rating")
    else:  # Default to featured (which we'll implement as newest)
        products = products.order_by("-date")
    
    context = {
        "vendor": vendor,
        "products": products,
        "current_sort": sort_by,
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
    sort_by = request.GET.get("sort", "featured")  # Default sort is featured
    
    products = Product.objects.filter(title__icontains=query)
    
    # Apply sorting based on the sort parameter
    if sort_by == "price_low_to_high":
        products = products.order_by("price")
    elif sort_by == "price_high_to_low":
        products = products.order_by("-price")
    elif sort_by == "release_date":
        products = products.order_by("-date")
    elif sort_by == "avg_rating":
        products = products.order_by("-rating")
    else:  # Default to featured (which we'll implement as newest)
        products = products.order_by("-date")

    context = {
        "products": products,
        "query": query,
        "current_sort": sort_by,
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


def save_checkout(request):
    cart_total_amount = 0

    # The variable below is completely dynamic, we're going to set it to zero
    # But when we start adding things into the cart the total_amount will begin to change value 
    # Depending on what the user has inside of their cart
    total_amount = 0

    # We want to grab the users information that he will input from: 
    # cart.html
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")

        print(full_name)
        print(email)
        print(mobile)
        print(address)
        print(city)
        print(state)
        print(country)

        # Now we want to save the users information during their shopping session
        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['mobile'] = mobile
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state
        request.session['country'] = country

        if 'cart_data_obj' in request.session:

            # Getting total amount for Paypal Amount
            for p_id, item in request.session['cart_data_obj'].items():
                total_amount += int(item['qty']) * float(item['price'])

            full_name = request.session['full_name']
            email = request.session['email']
            phone = request.session['mobile']
            address = request.session['address']
            city = request.session['city']
            state = request.session['state']
            country = request.session['country']

            # Create order Object
            order = CartOrder.objects.create(
                user=request.user,
                price=total_amount,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                country=country,
            )

            # After successfully collecting the information during the users session
            # and placing it into ORDER object we can then delete the data stored during the session
            del request.session['full_name']
            del request.session['email']
            del request.session['mobile']
            del request.session['address']
            del request.session['city']
            del request.session['state']
            del request.session['country']

            # Getting total amount for The Cart
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])

                cartOrderItems = CartOrderItems.objects.create(
                    order=order,
                    invoice_no="INVOICE_NO-" + str(order.id), # INVOICE_NO-5,
                    item=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price'])
                )
        return redirect("core:checkout", order.oid)
    return redirect("core:checkout", order.oid)


def checkout(request, oid):
    order = CartOrder.objects.get(oid=oid)
    order_items = CartOrderItems.objects.filter(order=order)

    ############ BELOW IS TO SUPPORT COUP FUNCTIONALITY ############
    if request.method == "POST":
        code = request.POST.get("code")
        print("code ========", code)
        coupon = Coupon.objects.filter(code=code, active=True).first()

        # Create a security mechanism for the coupon fearure: 
            # Add security message to notify user that coupon has been used "activated"
        if coupon:
            if coupon in order.coupons.all():
                messages.warning(request, "Coupon already activated")
                return redirect("core:checkout", order.oid)
            
            # otherwise, if not activated allow it to work
            else:
                # Calculation for superuser to create coupon in % form
                discount = order.price * coupon.discount / 100 
                order.coupons.add(coupon)
                order.price -= discount
                order.money_saved += discount
                order.save()

                messages.success(request, "Coupon Activated")
                return redirect("core:checkout", order.oid)
            
        # Prompt security message to notify user that coupon doesn't exist in our database
        else:
            messages.error(request, "Coupon Does Not Exists")
 
    context = {
        "order":order,
        "order_items":order_items,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, "core/checkout.html", context)

@login_required
def paypalCompletedView(request, oid):
    order = CartOrder.objects.get(oid=oid)
    if order.paid_status == False:
        order.paid_status == True
        order.save()

    context = {
        "order":order,
    }

    return render(request, 'core/payment-completed.html', context)

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
     order = CartOrder.objects.get(user=request.user, id=id)
     orderItems = CartOrderItems.objects.filter(order=order)

     context = {
         "order": order,
         "orderItems": orderItems,
     }
     return render(request, "core/order-detail.html", context)

def defaultAddress(request):
    id = request.GET['id']
    
    # Will make all other addresses deactivated (False)
    Address.objects.update(status=False)

    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean":True})


##################   WISHLIST    ##################
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


@csrf_exempt
def createCheckoutSession(request, oid):
    order = CartOrder.objects.get(oid=oid)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkoutSession = stripe.checkout.Session.create(
        customer_email = order.email,
        payment_method_types=['card'],

        line_items = [
            {
                'price_data': {
                    'currency': 'USD',
                    'product_data': {
                        'name': order.full_name
                    },
                    'unit_amount': int(order.price * 100)
                },
                'quantity': 1
            }
        ],
        mode = 'payment',
        
        # If payment succeeds, redirect the user to the payment-completed.html to notify them purchase has been successful
        # STRIPE EXPECTS TO LOOK FOR success_url, THEREFORE DON'T CHANGE IT 

        success_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid])) + "?session_id={CHECKOUT_SESSION_ID}",

        # If payment fails, redirect the user to the payment-failed.html to notify them about payment not going through 
        # STRIPE EXPECTS TO LOOK FOR cancel_url, THEREFORE DON'T CHANGE IT 
        cancel_url = request.build_absolute_uri(reverse("core:payment-failed"))
    )

    order.paid_status = False
    order.stripe_payment_intent = checkoutSession['id']
    order.save()

    print("checkkout session", checkoutSession)
    return JsonResponse({"sessionId": checkoutSession.id})
    
# We want the user to be logged in because it'll allow us to find out 
# which EXACT user sent the form, therefore we select the correct user to become vendor 

@login_required
def become_vendor(request):
    return render(request, "core/become-vendor.html")

@login_required
def vendor_application_form(request):
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    business_name = request.POST.get('business_name')
    business_description = request.POST.get('business_description')

    # Create vendor application with user association
    vendor_application = becomeVendorModel(
        user=request.user,  # Associate with the logged-in user
        full_name=full_name,
        email=email,
        phone=phone,
        business_name=business_name,
        business_description=business_description,
    )
    
    # Handle image uploads
    if 'vendor_profile_image' in request.FILES:
        vendor_application.vendor_profile_image = request.FILES['vendor_profile_image']
        
    if 'vendor_banner' in request.FILES:
        vendor_application.vendor_banner = request.FILES['vendor_banner']
    
    # Save the application with all data
    vendor_application.save()

    data = {
        "bool": True,
        "message": "Application Submitted Successfully! We'll review your details and contact you soon."
    }

    return JsonResponse({"data":data})

def aboutUs(request):
    return render(request, "core/about-me.html")

def purchasingGuide(request):
    return render(request, "core/purchasing-guide.html")