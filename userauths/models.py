# Create your models here.
##################################### READ BELOW ######################################################
# REMINDER: ANYTIME YOU MAKE A CHANGE HERE PLEASE DO THE FOLLOWING
#   1) python manage.py makemigrations
#   2) python manage.py migrate
#######################################################################################################
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save


# Define user_directory_path function first
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id if hasattr(instance, 'user') else 'vendor', filename)

# UserModel 
class User(AbstractUser):
    # We want to make sure that no one is using the same email for another account
    # Therefore we need to imply, unique = True 
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20)
    bio = models.CharField(max_length=100)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.username
    
# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image", null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    bio = models.CharField(max_length=300, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True) 
    address = models.CharField(max_length=200, null=True, blank=True) 
    country = models.CharField(max_length=60, null=True, blank=True) 
    verified = models.BooleanField(default=False, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.full_name} - {self.bio}"
    
# Contact Us Model 
# We will use this for a contact.html page
# This is where users will contact the website's admin and they have to 
class ContactUs(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.CharField(max_length=35)
    phone = models.CharField(max_length=15) 
    subject = models.CharField(max_length=30) 
    message = models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name
    

# We will use django signals to create a profile for a user when they sign up automatically. 
def create_user_profile(sender, instance, created, **kwargs):   #kwargs is Keyword arguments
    # When a new 
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

 
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)    

# After the ContactUs model, the becomeVendorForm is likely defined
# Let's fix it to use the user_directory_path function we just defined
class becomeVendorForm(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=100)
    business_description = models.TextField()
    vendor_profile_image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    vendor_banner = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Vendor Applications (Old)"
        
    def __str__(self):
        return self.business_name    