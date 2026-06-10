import hmac
import hashlib
import json
from decimal import Decimal
import requests
from django.conf import settings
from django.urls import reverse


def is_valid_paystack_signature(request):
    signature = request.headers.get('X-Paystack-Signature') or request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    if not signature:
        return False

    secret = settings.PAYSTACK_WEBHOOK_SECRET or settings.PAYSTACK_SECRET_KEY
    payload = request.body
    expected = hmac.new(secret.encode('utf-8'), payload, hashlib.sha512).hexdigest()
    return hmac.compare_digest(signature, expected)


def format_order_sms(order, payment=None):
    product_lines = []
    for item in order.items.all():
        product_lines.append(f"{item.product.name} x{item.quantity}")

    order_url = settings.SITE_URL.rstrip('/') + reverse('admin:orders_order_change', args=[order.id]) if hasattr(settings, 'SITE_URL') else ''

    lines = [
        f"New order received: #{order.id}",
        f"Customer: {order.first_name} {order.last_name}",
        f"Email: {order.email}",
    ]
    if getattr(order, 'phone', None):
        lines.append(f"Phone: {order.phone}")

    lines.extend([
        f"Total: {settings.CURRENCY_SYMBOL} {order.total}",
        f"Delivery: {order.get_delivery_option_display()}",
        f"Items: {', '.join(product_lines)}",
    ])
    if order_url:
        lines.append(f"Admin: {order_url}")

    if payment and payment.verified_at:
        lines.append(f"Paid at: {payment.verified_at:%Y-%m-%d %H:%M}")

    return '\n'.join(lines)


def send_sms_notification(order, payment=None, to_phone=None):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone = settings.TWILIO_FROM_PHONE
    to_phone = to_phone or settings.TWILIO_ADMIN_PHONE

    if not (account_sid and auth_token and from_phone and to_phone):
        return False

    message = format_order_sms(order, payment)
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    data = {
        'From': from_phone,
        'To': to_phone,
        'Body': message,
    }

    response = requests.post(url, auth=(account_sid, auth_token), data=data)
    response.raise_for_status()
    return True


def parse_paystack_amount(amount):
    if amount is None:
        return Decimal('0.00')
    return Decimal(amount) / Decimal('100')
