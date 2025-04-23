from django.urls import path, include # We need inlcude for paypal integration
from core.views import index, category_list_view, product_list_view, category_product_list_view, vendor_list_view, vendor_detail_view, product_detail_view, tag_list, add_review
from core.views import search_view, filter_product, add_to_cart, cart_view, delete_item_from_cart, update_cart, checkout, paypalCompletedView, paypalFailedView, createCheckoutSession
from core.views import  dashboard, orderDetail, defaultAddress, wishlistView, addToWishList, removeFromWishlist, contact, ajax_contact_form, save_checkout, vendor_application_form, become_vendor
from core.views import aboutUs, purchasingGuide
app_name = "core"

urlpatterns = [

    # Responsible for creating URL patterns on the browser
    # Example, bookstore.com/hardcover/special

    # We leave the bottom an empty string because we want the  
    # domain alone to direct us to the websites homepage

    # Views for Homepage
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("products/<pid>/", product_detail_view, name="product-detail"),

    # Views for Category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

    # Vendor Views
    path("vendors/", vendor_list_view, name="vendor-list"),
    path("vendors/<vid>/", vendor_detail_view, name="vendor-detail"),

    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),

    path("add-review/<pid>/", add_review, name="add-review"),

    path("search/", search_view, name="search"),
    path("filter-products/", filter_product, name = "filter-product"),

    #################### Cart Views  #################### 
    # Add to cart URL
    path("add-to-cart/", add_to_cart, name = "add-to-cart"),

    # Cart Page
    path("cart/",cart_view, name = "cart"),

    # Used when deleting items from cart
    path("delete-from-cart/", delete_item_from_cart, name = "delete-from-cart"),

    path("update-cart/", update_cart, name = "update-cart"),


    ####################  CHECKOUT VIEWS ####################
    # Checkout View
    path("checkout/<oid>/", checkout , name = "checkout"),

    # Save Checkout
    path("save_checkout_info/", save_checkout , name = "save_checkout_info"),

    # Additional Checkout: 
    # For stripe
    path("api/create_checkout_session/<oid>/", createCheckoutSession, name="api_checkout_session"),



    #################### Payment Views  #################### 
    # Paypal Views
    path('paypal/', include('paypal.standard.ipn.urls')),

    path('payment-completed/<oid>/', paypalCompletedView, name="payment-completed"),

    path('payment-failed/', paypalFailedView, name="payment-failed"),


    #################### User Info Views  #################### 
    # User Dashboard Views
    path('dashboard/', dashboard, name="dashboard"),
    path('dashboard/order/<int:id>', orderDetail, name="order-detail"),
    path("make-default-address/", defaultAddress , name="make-default-address"),


    #################### Wishlists Views  #################### 
    path ("wishlist/", wishlistView, name="wishlist"),
    path("add-to-wishlist/", addToWishList, name="add-to-wishlist"), 
    path("remove-from-wishlist/", removeFromWishlist, name="remove-from-wishlist"), 


    # Contact Views
    path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),


    path("become-vendor/", become_vendor, name="become-vendor"),
    path("vendor-application-form/", vendor_application_form, name="vendor-application-form"),

    path("about-me/", aboutUs, name="about-me"),
    path("purchasing-guide/", purchasingGuide, name="purchasing-guide"),
]