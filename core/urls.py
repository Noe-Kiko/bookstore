from django.urls import path
from core.views import index, category_list_view, product_list_view, category_product_list_view

app_name = "core"

urlpatterns = [

    # Responsible for creating URL patterns on the browser
    # Example, bookstore.com/hardcover/special

    # We leave the bottom an empty string because we want the  
    # domain alone to direct us to the websites homepage
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

]