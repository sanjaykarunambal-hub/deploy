from django.core.management.base import BaseCommand
from shop.models import Product


PRODUCTS = [
    dict(name="Aero Wireless Headphones", category="audio", price="49.99", old_price="64.99",
         rating="4.5", reviews=128, stock_status="in", image="images/headphones.svg",
         description="Comfortable over-ear wireless headphones with up to 20 hours of battery life, active noise isolation, and a foldable design for travel."),
    dict(name="Pulse Smart Watch", category="wearables", price="89.99", old_price=None,
         rating="4.2", reviews=64, stock_status="in", image="images/smartwatch.svg",
         description="Track steps, heart rate, sleep and notifications. Water resistant to 50m and pairs with both Android and iOS."),
    dict(name="Boom Bluetooth Speaker", category="audio", price="29.99", old_price="39.99",
         rating="4.0", reviews=89, stock_status="low", image="images/speaker.svg",
         description="Compact speaker with rich bass, 10-hour battery life, and a built-in microphone for hands-free calls."),
    dict(name='Nova 14" Laptop', category="computing", price="599.99", old_price=None,
         rating="4.6", reviews=41, stock_status="in", image="images/laptop.svg",
         description="14-inch laptop with 8GB RAM and 256GB SSD storage — fast enough for study, work, and everyday browsing."),
    dict(name="Core 20K Power Bank", category="power", price="19.99", old_price="24.99",
         rating="4.3", reviews=152, stock_status="in", image="images/powerbank.svg",
         description="10,000mAh portable charger with fast charging support, small enough to carry in your pocket."),
    dict(name="Drift Wireless Mouse", category="computing", price="14.99", old_price=None,
         rating="4.1", reviews=73, stock_status="in", image="images/mouse.svg",
         description="Ergonomic wireless mouse with adjustable DPI and a battery that lasts up to 6 months on a single charge."),
    dict(name="Tempo Earbuds Pro", category="audio", price="64.00", old_price="79.00",
         rating="4.4", reviews=97, stock_status="low", image="images/earbuds.svg",
         description="True wireless earbuds with active noise cancellation, sweat resistance, and a wireless charging case."),
    dict(name="Vertex Mechanical Keyboard", category="computing", price="79.00", old_price=None,
         rating="4.7", reviews=56, stock_status="in", image="images/keyboard.svg",
         description="Hot-swappable mechanical keyboard with per-key RGB lighting and a durable aluminum frame."),
]


class Command(BaseCommand):
    help = "Seeds the database with the starter VOLT Electronics product catalog."

    def handle(self, *args, **options):
        created_count = 0
        for data in PRODUCTS:
            _, created = Product.objects.get_or_create(name=data["name"], defaults=data)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {created_count} new product(s) created. "
            f"Total products in database: {Product.objects.count()}."
        ))
