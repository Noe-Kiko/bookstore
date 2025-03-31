from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishList, ProductImages, productReview, Address
from django.db.models import Min, Max, Count
def default(request):
    categories = Category.objects.all()
    address = None
    vendors = Vendor.objects.all()

    # 
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))
    
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
        'min_max_price':min_max_price,
    }