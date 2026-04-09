#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import Category, Product
from orders.models import Order, OrderItem
from datetime import datetime, timedelta
import random

# Get categories
shea = Category.objects.get(slug='shea-butter')
shampoo = Category.objects.get(slug='shampoo')
conditioner = Category.objects.get(slug='conditioner')
beard = Category.objects.get(slug='beard-oil')

# Create sample products
products_data = [
    (shea, 'Pure Shea Butter', 'Unrefined, raw shea butter from West Africa', 45.00, 18.00, 50),
    (shea, 'Whipped Shea Butter', 'Luxuriously whipped shea butter with vanilla essence', 55.00, 20.00, 40),
    (shampoo, 'Organic Cleansing Shampoo', 'Sulfate-free shampoo with natural botanicals', 35.00, 12.00, 60),
    (shampoo, 'Premium Argan Oil Shampoo', 'Rich shampoo infused with argan oil', 50.00, 18.00, 45),
    (conditioner, 'Deep Moisture Conditioner', 'Intensive conditioning treatment with coconut oil', 40.00, 15.00, 55),
    (conditioner, 'Silk Protein Conditioner', 'Luxury conditioner with silk proteins', 60.00, 22.00, 35),
    (beard, 'Beard Growth Oil', 'Stimulating beard oil with essential oils', 38.00, 14.00, 50),
    (beard, 'Premium Beard Serum', 'Luxury beard care serum', 65.00, 24.00, 30),
]

created_products = 0
for category, name, description, price, cost, stock in products_data:
    if not Product.objects.filter(name=name).exists():
        Product.objects.create(
            name=name,
            slug=name.lower().replace(' ', '-'),
            description=description,
            price=price,
            cost_price=cost,
            category=category,
            stock=stock,
            available=True
        )
        created_products += 1

print(f"Created {created_products} sample products.")

# Create sample orders
products = list(Product.objects.all())
created_orders = 0

for i in range(3):
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

print(f"Created {created_orders} sample orders.")
print("Sample data created successfully!")

def create_sample_batches():
    from analytics.models import ProductBatch, BatchMaterial
    from store.models import Product
    from decimal import Decimal
    import random
    from datetime import date, timedelta
    
    products = list(Product.objects.all())
    if not products:
        print("No products found. Create products first.")
        return
    
    created_batches = 0
    for _ in range(10):
        product = random.choice(products)
        batch_date = date.today() - timedelta(days=random.randint(0, 60))
        quantity_produced = random.randint(50, 200)
        
        batch = ProductBatch.objects.create(
            product=product,
            batch_date=batch_date,
            quantity_produced=quantity_produced,
            notes=f"Sample batch for {product.name}"
        )
        
        # Add some materials
        num_materials = random.randint(2, 5)
        for _ in range(num_materials):
            BatchMaterial.objects.create(
                batch=batch,
                name=f"Material {random.randint(1, 100)}",
                unit_cost=Decimal(random.uniform(10, 50)).quantize(Decimal('0.01')),
                quantity=Decimal(random.uniform(1, 10)).quantize(Decimal('0.01'))
            )
        
        created_batches += 1
    
    print(f"Created {created_batches} sample batches.")
