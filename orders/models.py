from decimal import Decimal
from django.conf import settings
from django.db import models
from store.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    DELIVERY_CHOICES = [
        ('delivery', 'Delivery'),
        ('collection', 'Collection at Star Mall CBD'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    exact_location = models.CharField(max_length=255, blank=True, null=True)
    house_number = models.CharField(max_length=50, blank=True, null=True)
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='delivery')
    distance_km = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.email}"

    def get_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_platform_fee(self):
        return (self.total * Decimal(settings.PLATFORM_FEE_PERCENT)) / Decimal('100')

    def get_profit(self):
        return self.total - self.get_cost() - self.get_platform_fee()
    
    def get_subtotal(self):
        """Get the subtotal (sum of all items excluding delivery fee)."""
        return sum(item.get_cost_per_item() for item in self.items.all())
    
    def get_paid_status(self):
        """Return payment status as human-readable string."""
        return "Paid" if self.paid else "Pending"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_cost(self):
        """Calculate cost to store (wholesale cost)."""
        return self.product.cost_price * self.quantity
    
    def get_cost_per_item(self):
        """Calculate total price for this item (selling price)."""
        return self.price * self.quantity
