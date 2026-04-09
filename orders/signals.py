from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order


@receiver(pre_save, sender=Order)
def store_original_status(sender, instance, **kwargs):
    """Store the original status before saving."""
    if instance.pk:
        try:
            original = Order.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Order.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None


@receiver(post_save, sender=Order)
def allocate_sales_on_fulfillment(sender, instance, created, **kwargs):
    """Allocate sales to batches when order is fulfilled."""
    if instance.status == 'fulfilled' and instance._original_status != 'fulfilled':
        for item in instance.items.all():
            item.product.allocate_sale(item.quantity)