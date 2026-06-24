from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),

    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/change/<int:pk>/", views.cart_change_qty, name="cart_change_qty"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("cart/summary.json", views.cart_summary_json, name="cart_summary_json"),

    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:pk>/", views.wishlist_toggle, name="wishlist_toggle"),

    path("checkout/", views.checkout_view, name="checkout"),
    path("order/<int:order_id>/success/", views.order_success, name="order_success"),

    path("contact/", views.contact_view, name="contact"),
]
