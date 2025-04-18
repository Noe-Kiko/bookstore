from django.contrib import admin
from userauths.models import User, Profile, ContactUs

# When reviewing users, we want to see a brief prompt of information about the user
# without having to redirect into a new page to get basic information (saves us time)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'bio']

class profileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'bio', 'phone']

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject']

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Profile, profileAdmin)
admin.site.register(ContactUs, ContactUsAdmin)