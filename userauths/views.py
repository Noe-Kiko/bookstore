from django.shortcuts import redirect, render
from userauths.forms import UserRegistrationForm
# Allow user toi be logged in automatically into site if signed up
from django.contrib.auth import login, authenticate
from django.contrib import messages 

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