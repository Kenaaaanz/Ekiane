from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import Payment
from .utils import send_sms_notification


@receiver(pre_save, sender=Payment)
def store_original_payment_status(sender, instance, **kwargs):
    """Store original payment status before saving for change detection."""
    if instance.pk:
        try:
            original = Payment.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Payment.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None


@receiver(post_save, sender=Payment)
def send_order_notification_email(sender, instance, created, **kwargs):
    """
    Send admin notification email and SMS when payment transitions to success.
    """
    if instance.status != 'success':
        return

    if getattr(instance, '_original_status', None) == 'success':
        return

    order = instance.order

    # Prepare context data for email template
    context = {
        'order': order,
        'payment': instance,
        'currency': settings.CURRENCY_SYMBOL,
        'platform_fee_percent': settings.PLATFORM_FEE_PERCENT,
        'admin_url': settings.SITE_URL + reverse('admin:orders_order_change', args=[order.id]) if hasattr(settings, 'SITE_URL') else '#',
    }

    # Render email templates
    html_message = render_to_string('emails/order_notification.html', context)
    text_message = render_to_string('emails/order_notification.txt', context)

    # Create email
    subject = f'New Order #{order.id} - {order.first_name} {order.last_name}'

    to_addresses = settings.ADMIN_EMAIL if isinstance(settings.ADMIN_EMAIL, list) else [settings.ADMIN_EMAIL]
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_addresses,
    )

    # Attach HTML version
    email.attach_alternative(html_message, "text/html")

    try:
        email.send(fail_silently=False)
        print(f"Order notification email sent for order #{order.id}")
    except Exception as e:
        print(f"Failed to send order notification email for order #{order.id}: {str(e)}")

    try:
        send_sms_notification(order, instance)
        print(f"Order SMS notification sent for order #{order.id}")
    except Exception as e:
        print(f"Failed to send order SMS notification for order #{order.id}: {str(e)}")
