from django.urls import path
from core.views import index

app_name = "core"

urlpatterns = [

    # Responsible for creating URL patterns on the browser
    # Example, bookstore.com/hardcover/special

    # We leave the bottom an empty string because we want the  
    # domain alone to direct us to the websites homepage
    path("", index)

]