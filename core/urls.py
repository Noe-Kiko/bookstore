from django.urls import path
from core.views import index, category_list_view, product_list_view, category_product_list_view, vendor_list_view, vendor_detail_view, product_detail_view, tag_list, add_review, search_view, filter_product, add_to_cart
app_name = "core"

urlpatterns = [

    # Responsible for creating URL patterns on the browser
    # Example, bookstore.com/hardcover/special

    # We leave the bottom an empty string because we want the  
    # domain alone to direct us to the websites homepage

    # Views for Homepage
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("products/<pid>", product_detail_view, name="product-detail"),

    # Views for Category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

    # Views for Vender
    path("vendors/", vendor_list_view, name="vendor-list"),
    path("vendors/<vid>", vendor_detail_view, name="vendor-detail"),

    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),

    path("add-review/<pid>/", add_review, name="add-review"),

    path("search/", search_view, name="search"),
    path("filter-products/", filter_product, name = "filter-product"),

    path("add-to-cart/", add_to_cart, name = "add-to-cart"),
]