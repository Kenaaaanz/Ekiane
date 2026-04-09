from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='products/', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])

    def allocate_sale(self, quantity):
        """Allocate sale quantity to open batches (FIFO)."""
        from analytics.models import ProductBatch
        remaining = quantity
        batches = ProductBatch.objects.filter(
            product=self, 
            status='open'
        ).order_by('open_date')
        
        for batch in batches:
            if remaining <= 0:
                break
            can_sell = min(remaining, batch.quantity_remaining)
            batch.sell_quantity(can_sell)
            remaining -= can_sell
        
        # Decrease stock
        self.stock = max(0, self.stock - quantity)
        self.save()