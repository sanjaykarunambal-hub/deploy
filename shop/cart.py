"""
Session-based shopping cart.

No user accounts are needed: Django gives every visitor a session
(tracked via a cookie), and we store the cart as a small dictionary
inside that session: {"<product_id>": quantity, ...}.

This replaces the old localStorage-based cart from the static version —
now the "source of truth" lives on the server, not in the browser.
"""

from decimal import Decimal
from .models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, product_id, quantity=1):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.save()

    def set_quantity(self, product_id, quantity):
        product_id = str(product_id)
        if quantity <= 0:
            self.remove(product_id)
        else:
            self.cart[product_id] = quantity
            self.save()

    def change_quantity(self, product_id, amount):
        product_id = str(product_id)
        current = self.cart.get(product_id, 0)
        self.set_quantity(product_id, current + amount)

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.cart.clear()
        self.save()

    def __iter__(self):
        """Yields dicts with product, quantity, and line_total — ready for templates."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_by_id = {str(p.id): p for p in products}

        for product_id, quantity in self.cart.items():
            product = products_by_id.get(product_id)
            if not product:
                continue  # product was deleted since being added to the cart
            yield {
                "product": product,
                "quantity": quantity,
                "line_total": product.price * quantity,
            }

    def __len__(self):
        return sum(self.cart.values())

    def get_total_price(self):
        total = Decimal("0.00")
        for item in self:
            total += item["line_total"]
        return total

    def get_total_items(self):
        return sum(self.cart.values())
