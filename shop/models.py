from django.db import models


class Product(models.Model):
    """A single item sold in the store. Managed through Django admin."""

    CATEGORY_CHOICES = [
        ("audio", "Audio"),
        ("wearables", "Wearables"),
        ("computing", "Computing"),
        ("power", "Power"),
    ]

    STOCK_CHOICES = [
        ("in", "In stock"),
        ("low", "Low stock"),
        ("out", "Out of stock"),
    ]

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    old_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Optional. Shown crossed out next to the price if set."
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    reviews = models.PositiveIntegerField(default=0)
    stock_status = models.CharField(max_length=10, choices=STOCK_CHOICES, default="in")
    image = models.CharField(
        max_length=200,
        help_text="Path under static/, e.g. images/headphones.svg"
    )
    description = models.TextField()
    is_active = models.BooleanField(default=True, help_text="Untick to hide from the store without deleting it.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def star_string(self):
        """Returns something like '★★★★☆' for templates."""
        full = round(float(self.rating))
        full = max(0, min(5, full))
        return "★" * full + "☆" * (5 - full)


class Order(models.Model):
    """A placed order. Created once at checkout; no login required."""

    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("card", "Credit / Debit Card"),
        ("upi", "UPI"),
    ]

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=80)
    zip_code = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
    subtotal = models.DecimalField(max_digits=9, decimal_places=2)
    shipping = models.DecimalField(max_digits=6, decimal_places=2)
    total = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} — {self.full_name}"

    @property
    def order_code(self):
        return f"VOLT-{self.id:06d}"

    @property
    def estimated_delivery(self):
        from datetime import timedelta
        return (self.created_at + timedelta(days=4)).strftime("%b %d")


class OrderItem(models.Model):
    """One product line inside an order, with the price locked in at purchase time."""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=120)  # kept even if the product is later deleted
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
