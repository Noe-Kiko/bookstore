from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishList, ProductImages, productReview, Address

def default(request):
    categories = Category.objects.all()
    return{
        'categories':categories
    }