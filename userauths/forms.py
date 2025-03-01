 # with the help of django forms, it saves us from the headache of using a ton of conditionals
# to create a proper sign up page. 
from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))

    # It's important to use .EmailField as it forces the user to input a string ending with @domain.com
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Username"}))

    # 
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}))

    class Meta:
        model = User
        fields = ['username', 'email']