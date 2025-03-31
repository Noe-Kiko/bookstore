from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishList, ProductImages, productReview, Address

def default(request):
    categories = Category.objects.all()
    address = None
    vendors = Vendor.objects.all()

    
    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None
        #or can write 
        # except:
        # address = None

    return{
        'categories':categories,
        'address':address, 
        'vendors':vendors,
    }