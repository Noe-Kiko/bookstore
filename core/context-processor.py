from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishList, ProductImages, productReview, Address

def default(request):
    categories = Category.objects.all()
    address = None
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(user=request.user)
        except Address.DoesNotExist:
            pass
        #or can write 
        # except:
        # address = None

    return{
        'categories':categories,
        'address':address, 
    }