from django.urls import path, include # We need inlcude for paypal integration
from core.views import index, category_list_view, product_list_view, category_product_list_view, vendor_list_view, vendor_detail_view, product_detail_view 
from core.views import tag_list, add_review, search_view, filter_product, add_to_cart, cart_view, delete_item_from_cart, update_cart, checkout_view
from core.views import paypalCompletedView, paypalFailedView, dashboard, orderDetail, defaultAddress

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

    # Add to cart URL
    path("add-to-cart/", add_to_cart, name = "add-to-cart"),

    # Cart Page
    path("cart/",cart_view, name = "cart"),

    # Used when deleting items from cart
    path("delete-from-cart/", delete_item_from_cart, name = "delete-from-cart"),

    path("update-cart/", update_cart, name = "update-cart"),

    path("checkout/", checkout_view, name = "checkout"),

    # Paypals URL
    path('paypal/', include('paypal.standard.ipn.urls')),

    path('payment-completed/', paypalCompletedView, name="payment-completed"),

    path('payment-failed/', paypalFailedView, name="payment-failed"),

    path('dashboard/', dashboard, name="dashboard"),

    path('dashboard/order/<int:id>', orderDetail, name="order-detail"),

    path("make-default-address/", defaultAddress , name="make-default-address"),

]