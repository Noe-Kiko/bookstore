# Create your models here.
##################################### READ BELOW ######################################################
# REMINDER: ANYTIME YOU MAKE A CHANGE HERE PLEASE DO THE FOLLOWING
#   1) python manage.py makemigrations
#   2) python manage.py migrate
#######################################################################################################
from django.db import models
from django.contrib.auth.models import AbstractUser

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
    
class Profile(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE) # Whenever a user get's deleted, we want to delete their profile
    image = models.ImageField(upload_to="image")
    full_Name = models.CharField(max_length=50, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=50)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_Name