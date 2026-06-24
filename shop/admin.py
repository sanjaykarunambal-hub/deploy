from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock_status", "is_active", "created_at")
    list_filter = ("category", "stock_status", "is_active")
    search_fields = ("name", "description")
    list_editable = ("price", "stock_status", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_code", "full_name", "email", "total", "payment_method", "created_at")
    list_filter = ("payment_method", "created_at")
    search_fields = ("full_name", "email")
    readonly_fields = ("subtotal", "shipping", "total", "created_at")
    inlines = [OrderItemInline]
