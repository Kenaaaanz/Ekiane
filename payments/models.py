from django.db import models
from orders.models import Order


class Payment(models.Model):
    STATUS_CHOICES = [
        ('initialized', 'Initialized'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initialized')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.reference} - {self.status}"
