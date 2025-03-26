from django.db import models
from unicodedata import decimal
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from pyexpat import model
from userauths.models import User

STATUS_CHOICE = {

    # Users should only see the right side
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
}

STATUS= {

    # Users should only see the right side
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("inReview", "In Review"),
    ("published", "Published"),
}

RATING= {

    # Users should only see the right side
    ( 1, "★☆☆☆☆"),
    ( 2, "★★☆☆☆"),
    ( 3, "★★★☆☆"),
    ( 4, "★★★★☆"),
    ( 5, "★★★★★"),
}

# Create your models here.
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="cat", alphabet="abcdefg12345")
    title = models.CharField(max_length=100, default="Category Item")
    
    # responsible for thumbnail of products
    image = models.ImageField(upload_to="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img sec= "%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title

class Tags(models.Model):
    pass
    
# Sort of like Amazon and TikTok shop where there are vendors to sell items too! 
class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="vendor", alphabet="abcdefg12345")

    title = models.CharField(max_length=100, default="Vendor name")
    image = models.ImageField(upload_to="user_directory_path", default="vendor.jpg")
    cover_image = models.ImageField(upload_to="user_directory_path", default="vendor.jpg")

    description = models.TextField(null = True, blank = True, default = "Describe yourself!")

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="user_directory_path")
    description = models.TextField(null = True, blank = True)
    
    address = models.CharField(max_length=100, default = "N/A")
    contact = models.CharField(max_length=100, default = "+1")
    chat_resp_time = models.CharField(max_length=100, default = "100")
    shipping_on_time = models.CharField(max_length=100, default = "100%")
    vendor_rating = models.CharField(max_length=100, default = "100")
    days_return = models.CharField(max_length=100, default="30")
    warranty_period = models.CharField(max_length=100, default="30")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe('<img sec= "%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=30, alphabet="abcdefg12345")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="products")
    title = models.CharField(max_length=100, default="Product Title")
    image = models.ImageField(upload_to="user_directory_path", default="product.jpg")
    description = models.TextField(null = True, blank = True, default = "The Product ")
    price = models.DecimalField(max_digits=9999999, decimal_places=2, default="9.99")
    old_price= models.DecimalField(max_digits=9999999, decimal_places=2, default="5.99")
    coverType = models.TextField(null = True, blank = True, default = "Hardcover")
    ###  
    subject = models.CharField(max_length=100, default="N/A", null=True, blank=True)
    isbn = models.CharField(max_length=100, default="N/A", null=True, blank=True)
    publishDate = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    ###
    tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=5, max_length=30, prefix = "sku", alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
            verbose_name_plural = "Products"

    def product_image(self):
            return mark_safe('<img sec= "%s" width="50" height="50" />' % (self.image.url))
        
    def __str__(self):
            return self.title
    
    def getPercentage(self):
         new_price = (self.price/ self.old_price) * 100

# Gives the ability to add MULTIPLE images to a single product
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images",on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
            verbose_name_plural = "Product Images"


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9999999, decimal_places=2, default="9.99")
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9999999, decimal_places=2, default="9.99")
    total = models.DecimalField(max_digits=9999999, decimal_places=2, default="9.99")

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_image(self):
        return mark_safe('<img sec= "/media/%s" width="50" height="50" />' % (self.image))
    

class productReview(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null = True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)
     
    class Meta:
            verbose_name_plural = "Product Reviews"
    
    def __str__(self):
            return self.product.title
    
    def get_rating(self):
         return self.rating
    


class wishList(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null = True)
    date = models.DateTimeField(auto_now_add=True)
     
    class Meta:
            verbose_name_plural = "Wishlists"
    
    def __str__(self):
            return self.product.title

class Address(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    address = models.CharField(max_length=100, null = True)
    status = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Address"