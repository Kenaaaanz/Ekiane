from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from store.models import Product


class ProductBatch(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_date = models.DateField()
    quantity_produced = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    quantity_sold = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    open_date = models.DateTimeField(default=timezone.now)
    close_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-batch_date']
        verbose_name = 'Product Batch'
        verbose_name_plural = 'Product Batches'

    def __str__(self):
        return f"{self.product.name} batch on {self.batch_date} ({self.status})"

    def sell_quantity(self, qty):
        """Record sale of qty items from this batch."""
        self.quantity_sold += qty
        if self.quantity_sold >= self.quantity_produced and self.status == 'open':
            self.close_batch()
        self.save()

    def close_batch(self):
        """Close the batch when sold out."""
        from django.utils import timezone
        self.status = 'closed'
        self.close_date = timezone.now()
        self.save()

    @property
    def quantity_remaining(self):
        return self.quantity_produced - self.quantity_sold

    @property
    def is_closed(self):
        return self.status == 'closed'

    @property
    def days_open(self):
        from django.utils import timezone
        end_date = self.close_date or timezone.now()
        return (end_date - self.open_date).days

    def total_revenue(self):
        return self.quantity_sold * self.product.price

    def total_profit(self):
        revenue = self.total_revenue()
        cost = self.material_cost()
        return revenue - cost

    def profit_per_day(self):
        if self.days_open > 0:
            return self.total_profit() / Decimal(self.days_open)
        return Decimal('0.00')

    def profit_per_month(self):
        months = Decimal(self.days_open) / Decimal(30)
        if months > 0:
            return self.total_profit() / months
        return Decimal('0.00')

    def time_to_sell_out(self):
        """Days to sell the entire batch."""
        if self.is_closed and self.close_date:
            return (self.close_date - self.open_date).days
        return None

    def material_cost(self):
        material_total = sum(material.total_cost for material in self.materials.all())
        return material_total or Decimal('0.00')

    def cost_per_unit(self):
        if self.quantity_produced:
            return self.material_cost() / Decimal(self.quantity_produced)
        return self.material_cost()

    def product_cost(self):
        return self.product.cost_price or Decimal('0.00')

    def cost_variance(self):
        return self.material_cost() - self.product_cost()

    def profit_margin(self):
        if self.product.price and self.product.price != Decimal('0.00'):
            return ((self.product.price - self.cost_per_unit()) / self.product.price) * Decimal('100')
        return Decimal('0.00')

    @property
    def sell_through_rate(self):
        """Percentage of batch sold."""
        if self.quantity_produced > 0:
            return (self.quantity_sold / self.quantity_produced) * 100
        return 0


class BatchMaterial(models.Model):
    batch = models.ForeignKey(ProductBatch, related_name='materials', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    class Meta:
        verbose_name = 'Batch Material'
        verbose_name_plural = 'Batch Materials'

    def __str__(self):
        return self.name

    @property
    def total_cost(self):
        if self.unit_cost is None or self.quantity is None:
            return Decimal('0.00')
        return self.unit_cost * self.quantity
