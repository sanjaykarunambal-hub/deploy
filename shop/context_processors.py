"""
Makes the cart and wishlist available in every template automatically —
used for the navbar badges and the slide-out cart drawer that appear
on every page, without repeating the same lookup in every view.
"""

from .cart import Cart
from .wishlist import Wishlist


def cart_and_wishlist(request):
    cart = Cart(request)
    wishlist = Wishlist(request)
    return {
        "cart_count": cart.get_total_items(),
        "wishlist_count": len(wishlist),
        "drawer_cart_items": list(cart),
        "drawer_cart_total": cart.get_total_price(),
    }
