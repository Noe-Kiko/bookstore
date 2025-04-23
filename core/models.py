from django.db import models
from unicodedata import decimal
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from pyexpat import model
from userauths.models import User
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field

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
########################
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
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title

########################
class Tags(models.Model):
    pass

########################

# Inside of /admin/ the moderator(superuser) will have to fill out form for user to become a vendor
class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="vendor", alphabet="abcdefg12345")

    vendor_title = models.CharField(max_length=100, default="Vendor name")
    vendor_profile_image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    vendor_banner = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")

    description = CKEditor5Field(null = True, blank = True, default = "Describe yourself!")
    
    vendor_address = models.CharField(max_length=100, default = "Vendor's Address")
    vendor_mobile = models.CharField(max_length=100, default = "(732) - 123 - 4567")
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.vendor_profile_image.url))
    
    def __str__(self):
        return self.vendor_title
    
########################
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=30, alphabet="abcdefg12345")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="products")
    title = models.CharField(max_length=100, default="Fahrenheit 451")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = CKEditor5Field(null = True, blank = True, default = "Here feel free to write anything about the book! Such as the wear, edition, covertype, and etc!")

    ###### CHANGED DEFAULT FROM FLOAT TO STR #####
    price = models.DecimalField(max_digits=10, decimal_places=2, default="9.99")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default="5.99")
       
    publishDate = models.CharField(max_length=100, default="todays date")
    stock_count = models.CharField(max_length=100, default="N/A", null=True, blank=True)
    condition = models.CharField(max_length=100, default="used", null=True, blank=True)

    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
            verbose_name_plural = "Products"

    def product_image(self):
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
        
    def __str__(self):
            return self.title
    
    def getPercentage(self):
         new_price = (self.price/ self.old_price) * 100

########################
# Gives the ability to add MULTIPLE images to a single product
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images",on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
            verbose_name_plural = "Product Images"

########################
class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Put models from cart page in here 
    full_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)

    shipping_method = models.CharField(max_length=50, null=True, blank=True)
    trackingId = models.CharField(max_length=50, null=True, blank=True)
    trackingWebsite = models.CharField(max_length=50, null=True, blank=True)

    price = models.DecimalField(max_digits=9, decimal_places=2, default=9.99)
    money_saved = models.CharField(max_length=50, null=True, default=0.00)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing", null=True, blank=True)

    # The bookstore is a marketplace, therefore if we have any vendors who are selling books 
    # as their full time job, we want to provide features to help them organize or manage their inventory
    # The Custom label is sort of like SKU's
    custom_label = ShortUUIDField(null=True, blank=True, length=5, max_length=20,)
    oid = ShortUUIDField(null=True, blank=True, length=5, max_length=20, alphabet="123456789")

    # Adding Coupon Feature
    coupons = models.ManyToManyField("core.Coupon", blank=True)
    class Meta:
        verbose_name_plural = "Cart Order"

########################
class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default="0.00")
    total = models.DecimalField(max_digits=9, decimal_places=2, default="0.00")

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))
    
########################
class productReview(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null = True, related_name = 'review')
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)
     
    class Meta:
            verbose_name_plural = "Product Reviews"
    
    def __str__(self):
            return self.product.title
    
    def get_rating(self):
         return self.rating
    

########################
class wishListModel(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null = True)
    date = models.DateTimeField(auto_now_add=True)
     
    class Meta:
            verbose_name_plural = "Wishlists"
    
    def __str__(self):
            return self.product.title

########################
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mobile = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"

########################
class Coupon(models.Model):
    code = models.CharField(max_length=15)
    discount = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code}"

########################
# Path for vendor application uploads
def vendor_application_path(instance, filename):
    # Use the business name in the path for better organization
    business_name = instance.business_name.replace(" ", "_").lower()
    return 'vendor_applications/{0}/{1}'.format(business_name, filename)

########################
class becomeVendorModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="vendor_applications")  # Store the user who applied
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=100)
    business_description = models.TextField()
    vendor_profile_image = models.ImageField(upload_to=vendor_application_path, default="vendor.jpg")
    vendor_banner = models.ImageField(upload_to=vendor_application_path, default="vendor.jpg")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Vendor Applications"
        
    def __str__(self):
        return f"{self.business_name} by {self.user.username if self.user else 'Unknown'}"
