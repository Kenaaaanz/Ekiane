"""
Management command to sync payment statuses with Paystack.
Handles transactions that completed on Paystack but webhook didn't fire.
"""
import requests
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from payments.models import Payment
from orders.models import Order
from payments.utils import parse_paystack_amount


class Command(BaseCommand):
    help = 'Sync payment statuses with Paystack API to catch missed webhooks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Number of pending payments to check (default: 50)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Check payments created in last N days (default: 7)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        days = options['days']
        
        # Get pending payments from last N days
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        pending_payments = Payment.objects.filter(
            status='initialized',
            created_at__gte=cutoff_date
        ).order_by('-created_at')[:limit]
        
        self.stdout.write(f"Found {pending_payments.count()} pending payments to check")
        
        synced = 0
        failed = 0
        already_processed = 0
        
        for payment in pending_payments:
            result = self._check_payment_status(payment)
            if result == 'synced':
                synced += 1
            elif result == 'failed':
                failed += 1
            elif result == 'already_processed':
                already_processed += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSync complete:\n"
                f"  Synced: {synced}\n"
                f"  Already processed: {already_processed}\n"
                f"  Failed to sync: {failed}"
            )
        )

    def _check_payment_status(self, payment):
        """Check payment status via Paystack API and update if needed"""
        try:
            headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
            response = requests.get(
                f'https://api.paystack.co/transaction/verify/{payment.reference}',
                headers=headers,
                timeout=10
            )
            data = response.json()
            
            if not data.get('status'):
                self.stdout.write(
                    f"  ✗ {payment.reference}: API error - {data.get('message', 'Unknown error')}"
                )
                return 'failed'
            
            paystack_status = data['data'].get('status')
            
            if paystack_status == 'success' and payment.status != 'success':
                # Payment succeeded on Paystack but not updated in our system
                payment_data = data['data']
                payment.status = 'success'
                payment.verified_at = timezone.now()
                payment.save()
                
                # Update order
                order = payment.order
                if order.status != 'paid':
                    order.paid = True
                    order.status = 'paid'
                    order.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ {payment.reference}: Synced to SUCCESS (order #{order.id})"
                        )
                    )
                    return 'synced'
                else:
                    self.stdout.write(
                        f"  ℹ {payment.reference}: Already marked as paid"
                    )
                    return 'already_processed'
            
            elif paystack_status == 'failed' and payment.status != 'failed':
                payment.status = 'failed'
                payment.save()
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ {payment.reference}: Marked as FAILED on Paystack"
                    )
                )
                return 'synced'
            
            else:
                self.stdout.write(
                    f"  ℹ {payment.reference}: Status unchanged ({paystack_status})"
                )
                return 'already_processed'
        
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(
                    f"  ✗ {payment.reference}: Network error - {str(e)}"
                )
            )
            return 'failed'
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"  ✗ {payment.reference}: Error - {str(e)}"
                )
            )
            return 'failed'
