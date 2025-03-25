# Responsible for redirecting users to other pages and rendering the pages
from django.shortcuts import redirect, render
from userauths.forms import UserRegistrationForm

# Allow user to be logged in automatically into site if signed up
from django.contrib.auth import authenticate, login

#Responsible for logging the user out of their account
from django.contrib.auth import logout

# Responsible for prompting urgent messages
from django.contrib import messages 

from django.conf import settings
# Fix for user login bug
from userauths.models import User

# What is the point of this variable? Well if you go to bookstore/settings.py 
# you'll scroll down and find AUTH_USER_MODEL which is connected to "userauths.User"
# We will use this for our try catch 
User = settings.AUTH_USER_MODEL

# Create your views here.

def registerView(request):

    if request.method == "POST":
        form = UserRegistrationForm(request.POST or None)

        # Responsible for checking if signup data is valid and not malicious data
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")

            # We want to give a quick prompt that the account was created succesfully
            messages.success(request, f"Hey {username}, Your account was created successfully!")
            

            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1']
            
            )
            login(request, new_user)
            # After logging in the new user, redirect them to the index page
            return redirect("core:index")
    else: 
        form = UserRegistrationForm()
        

    
    context = {
        'form': form,
    }
    return render(request, "userauths/sign-up.html", context)

def loginView(request):
    # If a user is already logged in, we want to redirect them to the homepage
    if request.user.is_authenticated:
        messages.warning(request, f"Hey, you're already logged in!")
        return redirect("core:index")
    
    if request.method == "POST":

        # Below is basically the same as; email = form = LoginForm(request.POST)
        # It grabs the email the user inputs
        email = request.POST.get("email")
        password = request.POST.get("password")

        ######### PLEASE PUT IN A TRY-CATCH #########
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in.")
                return redirect("core:index")
            else: 
                messages.warning(request, "User Does Not Exist, create an account.")

        except:
            messages.warning(request, f"User with {email} doesn't exist!")

    context = {

    }

    return render(request, "userauths/sign-in.html")


def logoutView(request):
      logout(request)
      messages.success(request, "You logged out.")
      return redirect("userauths:sign-in")