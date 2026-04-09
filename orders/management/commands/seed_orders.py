from django.core.management.base import BaseCommand
from orders.models import Order, OrderItem
from store.models import Product
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample orders for analytics dashboard'

    def handle(self, *args, **options):
        products = list(Product.objects.all())
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Create products first.'))
            return

        created_orders = 0
        for i in range(5):
            # Create orders on different dates
            order_date = datetime.now() - timedelta(days=random.randint(1, 28))

            order = Order.objects.create(
                email=f"customer{i}@example.com",
                first_name="Sample",
                last_name=f"Customer {i}",
                address="123 Main Street",
                city="Nairobi",
                postal_code="00100",
                paid=True,
                status='fulfilled',
                created_at=order_date
            )

            # Add random items to order
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )

            order.total = sum(item.price * item.quantity for item in order.items.all())
            order.save()
            created_orders += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_orders} sample orders'))
