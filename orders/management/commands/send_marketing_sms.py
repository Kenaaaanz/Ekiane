from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from payments.utils import send_twilio_sms


class Command(BaseCommand):
    help = 'Send custom marketing SMS to customer phone numbers collected from orders.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--message',
            type=str,
            required=True,
            help='The SMS message body to send to customers.',
        )
        parser.add_argument(
            '--phones',
            type=str,
            default='',
            help='Comma-separated list of additional phone numbers to include.',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Send to customers with orders in the last N days (default: 30).',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Optional limit on number of recipients (0 = no limit).',
        )
        parser.add_argument(
            '--include-cancelled',
            action='store_true',
            help='Include cancelled orders in the recipient list.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which phone numbers would receive the message without sending.',
        )

    def handle(self, *args, **options):
        message = options['message'].strip()
        if not message:
            self.stderr.write(self.style.ERROR('The --message parameter cannot be empty.'))
            return

        cutoff = timezone.now() - timedelta(days=options['days'])
        orders = Order.objects.filter(phone__isnull=False).exclude(phone='').filter(created_at__gte=cutoff)
        if not options['include_cancelled']:
            orders = orders.exclude(status='cancelled')

        phone_numbers = set(order.phone.strip() for order in orders if order.phone and order.phone.strip())

        if options['phones']:
            extra = [part.strip() for part in options['phones'].split(',') if part.strip()]
            phone_numbers.update(extra)

        if not phone_numbers:
            self.stderr.write(self.style.ERROR('No phone numbers found to send marketing SMS.'))
            return

        phone_list = list(phone_numbers)
        if options['limit'] > 0:
            phone_list = phone_list[:options['limit']]

        self.stdout.write(self.style.SUCCESS(f'Preparing to send marketing SMS to {len(phone_list)} phone number(s).'))

        if options['dry_run']:
            for phone in phone_list:
                self.stdout.write(f'Would send to: {phone}')
            return

        sent = 0
        failed = 0

        for phone in phone_list:
            try:
                send_twilio_sms(phone, message)
                self.stdout.write(self.style.SUCCESS(f'Sent to {phone}'))
                sent += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed {phone}: {e}'))
                failed += 1

        self.stdout.write(self.style.SUCCESS(f'Finished sending marketing SMS: {sent} sent, {failed} failed.'))
