from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import Payment


@receiver(post_save, sender=Payment)
def send_order_notification_email(sender, instance, created, **kwargs):
    """
    Send admin notification email when payment is successfully verified.
    Only send on payment success to avoid duplicate emails.
    """
    # Only send email if payment status is 'success'
    if instance.status != 'success':
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
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_EMAIL],
    )
    
    # Attach HTML version
    email.attach_alternative(html_message, "text/html")
    
    # Send email
    try:
        email.send(fail_silently=False)
        print(f"Order notification email sent for order #{order.id}")
    except Exception as e:
        print(f"Failed to send order notification email for order #{order.id}: {str(e)}")
