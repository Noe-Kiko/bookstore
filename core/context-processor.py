from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishListModel, ProductImages, productReview, Address
from django.db.models import Min, Max, Count
from django.db import DatabaseError
from django.contrib import messages

def default(request):
    try:
        categories = Category.objects.all()
    except DatabaseError:
        categories = []
        
    try:
        vendors = Vendor.objects.all()
    except DatabaseError:
        vendors = []

    # Try to get min/max price, handle if table doesn't exist
    try:
        min_max_price = Product.objects.aggregate(Min("price"), Max("price"))
    except DatabaseError:
        min_max_price = {'price__min': 0, 'price__max': 1000}
    
    # if the user is successfully authenitcated (login)
    # We want to be able to fetch the users saved wishlist data
    wishlist = 0
    if request.user.is_authenticated:
        try:
            wishlist = wishListModel.objects.filter(user=request.user)
        except DatabaseError:
            # Don't show message here since it will appear on every page load
            pass

    # Try to get user address
    address = None
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(user=request.user)
        except:
            pass

    return{
        'categories':categories,
        'wishlist':wishlist,
        'address':address, 
        'vendors':vendors,
        'min_max_price':min_max_price,
    }