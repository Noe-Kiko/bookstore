from django.urls import path
from userauths import views

app_name = "userauths"

'''
# Inside of Basic URL Patterns you'll see: 
    # 1) Sign-up page
    # 2) Sign-in page
    # 3) Sign-out page

These URL patterns are responsible for the absolute basics of user functionality
'''
urlpatterns = [
    # Basic URL patterns
    path("sign-up/", views.registerView, name="sign-up"),
    path("sign-in/", views.loginView, name="sign-in"),
    path("sign-out/", views.logoutView, name="sign-out"),

    # URL below is responsible for updating user's profile
    path("profile/update/", views.profileUpdate, name="profile-update"),

]
