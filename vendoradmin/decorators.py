from django.contrib import messages
from django.shortcuts import redirect


'''
Below is a custom decorator that I wrote: 

'''
def adminRequired(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser != True:
            messages.warning(request, "You're not authorized!")
            return redirect("/user/sign-in/")
        return view_func(request, *args, **kwargs)

    return wrapper