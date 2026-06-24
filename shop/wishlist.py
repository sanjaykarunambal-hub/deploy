"""
Session-based wishlist — same idea as the cart, just a list of product IDs.
"""

from .models import Product

WISHLIST_SESSION_KEY = "wishlist"


class Wishlist:
    def __init__(self, request):
        self.session = request.session
        wishlist = self.session.get(WISHLIST_SESSION_KEY)
        if wishlist is None:
            wishlist = self.session[WISHLIST_SESSION_KEY] = []
        self.wishlist = wishlist

    def save(self):
        self.session[WISHLIST_SESSION_KEY] = self.wishlist
        self.session.modified = True

    def toggle(self, product_id):
        """Adds if missing, removes if present. Returns True if now wishlisted."""
        product_id = str(product_id)
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            self.save()
            return False
        else:
            self.wishlist.append(product_id)
            self.save()
            return True

    def contains(self, product_id):
        return str(product_id) in self.wishlist

    def get_products(self):
        return Product.objects.filter(id__in=self.wishlist)

    def __len__(self):
        return len(self.wishlist)
