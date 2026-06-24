from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Order, OrderItem
from .cart import Cart
from .wishlist import Wishlist

FREE_SHIPPING_THRESHOLD = Decimal("50.00")
SHIPPING_COST = Decimal("4.99")


def _cart_summary(cart):
    """Shared subtotal/shipping/total calculation used by cart + checkout views."""
    subtotal = cart.get_total_price()
    shipping = Decimal("0.00") if subtotal == 0 or subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
    return subtotal, shipping, subtotal + shipping


def home(request):
    products = Product.objects.filter(is_active=True)

    category = request.GET.get("category", "all")
    if category != "all":
        products = products.filter(category=category)

    search = request.GET.get("q", "").strip()
    if search:
        products = products.filter(name__icontains=search)

    sort = request.GET.get("sort", "default")
    if sort == "price-asc":
        products = products.order_by("price")
    elif sort == "price-desc":
        products = products.order_by("-price")
    elif sort == "rating":
        products = products.order_by("-rating")

    wishlist = Wishlist(request)

    context = {
        "products": products,
        "active_category": category,
        "search": search,
        "sort": sort,
        "result_count": products.count(),
        "wishlist_ids": wishlist.wishlist,
    }
    return render(request, "shop/home.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=pk)[:4]
    wishlist = Wishlist(request)

    context = {
        "product": product,
        "related": related,
        "is_wishlisted": wishlist.contains(product.id),
    }
    return render(request, "shop/product_detail.html", context)


# ---------------------------------------------------------------------------
# CART — every action saves into the Django session on the server.
# ---------------------------------------------------------------------------

def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart = Cart(request)
    qty = int(request.POST.get("quantity", 1))
    cart.add(product.id, qty)
    messages.success(request, f"{product.name} added to your cart.")
    return redirect(request.POST.get("next", "shop:home"))


def cart_change_qty(request, pk):
    cart = Cart(request)
    amount = int(request.POST.get("amount", 1))
    cart.change_quantity(pk, amount)
    return redirect("shop:cart")


def cart_remove(request, pk):
    cart = Cart(request)
    cart.remove(pk)
    messages.info(request, "Item removed from your cart.")
    return redirect("shop:cart")


def cart_view(request):
    cart = Cart(request)
    subtotal, shipping, total = _cart_summary(cart)

    context = {
        "cart_items": list(cart),
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "free_shipping_threshold": FREE_SHIPPING_THRESHOLD,
    }
    return render(request, "shop/cart.html", context)


# ---------------------------------------------------------------------------
# WISHLIST
# ---------------------------------------------------------------------------

def wishlist_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist = Wishlist(request)
    now_active = wishlist.toggle(product.id)
    if now_active:
        messages.success(request, f"{product.name} saved to your wishlist.")
    else:
        messages.info(request, f"{product.name} removed from your wishlist.")
    return redirect(request.POST.get("next", "shop:home"))


def wishlist_view(request):
    wishlist = Wishlist(request)
    context = {"products": wishlist.get_products()}
    return render(request, "shop/wishlist.html", context)


# ---------------------------------------------------------------------------
# CHECKOUT — actually saves a real Order + OrderItem rows to the database.
# ---------------------------------------------------------------------------

def checkout_view(request):
    cart = Cart(request)
    subtotal, shipping, total = _cart_summary(cart)

    if request.method == "POST":
        if len(cart) == 0:
            messages.error(request, "Your cart is empty.")
            return redirect("shop:cart")

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        zip_code = request.POST.get("zip_code", "").strip()
        payment_method = request.POST.get("payment_method", "cod")

        errors = {}
        if not full_name:
            errors["full_name"] = "Enter your full name."
        if not email or "@" not in email:
            errors["email"] = "Enter a valid email address."
        if not address:
            errors["address"] = "Enter your delivery address."
        if not city:
            errors["city"] = "Enter your city."
        if not zip_code:
            errors["zip_code"] = "Enter a valid PIN/ZIP code."

        if errors:
            messages.error(request, "Please fix the highlighted fields.")
            context = {
                "cart_items": list(cart),
                "subtotal": subtotal,
                "shipping": shipping,
                "total": total,
                "free_shipping_threshold": FREE_SHIPPING_THRESHOLD,
                "errors": errors,
                "form_data": request.POST,
            }
            return render(request, "shop/checkout.html", context)

        # Create the order and its line items
        order = Order.objects.create(
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            zip_code=zip_code,
            payment_method=payment_method,
            subtotal=subtotal,
            shipping=shipping,
            total=total,
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                product_name=item["product"].name,
                unit_price=item["product"].price,
                quantity=item["quantity"],
            )

        cart.clear()
        return redirect("shop:order_success", order_id=order.id)

    context = {
        "cart_items": list(cart),
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "free_shipping_threshold": FREE_SHIPPING_THRESHOLD,
        "errors": {},
        "form_data": {},
    }
    return render(request, "shop/checkout.html", context)


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "shop/order_success.html", {"order": order})


# ---------------------------------------------------------------------------
# CONTACT — validated server-side; doesn't actually send email (no SMTP
# configured), but the pattern is real and ready to wire up later.
# ---------------------------------------------------------------------------

def contact_view(request):
    errors = {}
    sent = False

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name:
            errors["name"] = "Please enter your name."
        if not email or "@" not in email:
            errors["email"] = "Please enter a valid email."
        if len(message) < 10:
            errors["message"] = "Message should be at least 10 characters."

        if not errors:
            sent = True

    context = {"errors": errors, "sent": sent}
    return render(request, "shop/contact.html", context)


# ---------------------------------------------------------------------------
# Small JSON endpoint used by the navbar to refresh cart/wishlist counts
# without a full page reload (used by the cart drawer).
# ---------------------------------------------------------------------------

def cart_summary_json(request):
    cart = Cart(request)
    wishlist = Wishlist(request)
    return JsonResponse({
        "cart_count": cart.get_total_items(),
        "wishlist_count": len(wishlist),
    })
