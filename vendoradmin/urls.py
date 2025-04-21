from django.urls import path
from vendoradmin.views import vendorDashboard, vendorsProducts, addProducts, editProduct, deleteProduct
from vendoradmin.views import orders, orderDetail, changeOrderStatus, shopPage, reviews, settings, changePassword

app_name = "vendoradmin"

urlpatterns = [
    path("dashboard/", vendorDashboard, name="dashboard"),
    path("products/", vendorsProducts, name="products"),
    path("add_product/", addProducts, name="add_product"),
    path("edit_product/<pid>/", editProduct, name="edit_product"),
    path("delete_product/<pid>/", deleteProduct, name="delete_product"),
    path("orders/", orders, name="orders"),
    path("order_detail/<id>/", orderDetail, name="order_detail"),
    path("change_order_status/<oid>/", changeOrderStatus, name="change_order_status"),
    path("shop_page/", shopPage, name="shop_page"),
    path("reviews/", reviews, name="reviews"),
    path("settings/", settings, name="settings"),
    path("change_password/", changePassword, name="change_password"),
]
