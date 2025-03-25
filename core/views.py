from django.shortcuts import render
from django.http import HttpResponse
from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishList, ProductImages, productReview, Address

# Create your views here.
def index(request):
    # product = Product.objects.all().order_by("-id")
    product = Product.objects.filter(product_status="published", featured = True)
    context = {
        "products":product
    }    

    return render(request, 'core/index.html', context)   