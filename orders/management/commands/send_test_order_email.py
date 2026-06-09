"""
Send a test order notification email to the admin.
This helps verify that email configuration is working correctly.
"""

from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from orders.models import Order, OrderItem
from payments.models import Payment
from store.models import Product


class Command(BaseCommand):
    help = 'Send a test order notification email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order-id',
            type=int,
            help='Order ID to send email for. If not provided, creates a test order.',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send to (overrides admin email)',
        )

    def handle(self, *args, **options):
        order_id = options.get('order_id')
        email = options.get('email') or settings.ADMIN_EMAIL

        if order_id:
            try:
                order = Order.objects.get(pk=order_id)
                self.stdout.write(f"Using order #{order_id}")
            except Order.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Order #{order_id} not found'))
                return
        else:
            # Create a test order
            self.stdout.write("Creating test order...")
            order = Order.objects.create(
                email='customer@example.com',
                first_name='Test',
                last_name='Customer',
                phone='+1234567890',
                exact_location='123 Test Street',
                house_number='123',
                delivery_option='delivery',
                distance_km=5,
                delivery_fee=200,
                status='paid',
                paid=True,
                total=1500,
            )
            
            # Add a test item
            try:
                product = Product.objects.first()
                if product:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=1300,
                        quantity=1,
                    )
            except:
                pass

        # Try to get payment if exists
        try:
            payment = Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            payment = None
            
        # Prepare context
        context = {
            'order': order,
            'payment': payment,
            'currency': settings.CURRENCY_SYMBOL,
            'platform_fee_percent': settings.PLATFORM_FEE_PERCENT,
            'admin_url': settings.SITE_URL + reverse('admin:orders_order_change', args=[order.id]) 
                        if hasattr(settings, 'SITE_URL') else '#',
        }
        
        # Render templates
        html_message = render_to_string('emails/order_notification.html', context)
        text_message = render_to_string('emails/order_notification.txt', context)
        
        # Create email
        subject = f'Test Order Notification - Order #{order.id}'
        
        email_obj = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        
        email_obj.attach_alternative(html_message, "text/html")
        
        # Send
        try:
            email_obj.send(fail_silently=False)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Test email sent successfully to {email}')
            )
            self.stdout.write(f'  Subject: {subject}')
            self.stdout.write(f'  Order: #{order.id}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send email: {str(e)}')
            )
