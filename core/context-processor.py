from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, wishListModel, ProductImages, productReview, Address
from django.db.models import Min, Max, Count
def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()

    # 
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))
    
    # if the user is successfully authenitcated (login)
    # We want to be able to fetch the users saved wishlist data
    if request.user.is_authenticated:
        try:
            wishlist = wishListModel.objects.filter(user=request.user)
        except:
            messages.warning(request, "You need to login before accessing your wishlist.")
            wishlist = 0
    # If the user isn't authenticated then theres no reason to fetch data from the database
    else:
        wishlist = 0

    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None
        #or can write 
        # except:
        # address = None

    return{
        'categories':categories,
        'wishlist':wishlist,
        'address':address, 
        'vendors':vendors,
        'min_max_price':min_max_price,
    }