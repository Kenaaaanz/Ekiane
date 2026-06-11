import hmac
import hashlib
import json
from decimal import Decimal
import requests
from django.conf import settings
from django.urls import reverse


def _normalize_phone_list(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [phone.strip() for phone in value if phone and phone.strip()]
    return [phone.strip() for phone in str(value).split(',') if phone.strip()]


def get_twilio_admin_numbers():
    return _normalize_phone_list(settings.TWILIO_ADMIN_PHONE)


def send_twilio_sms(to_phone, body):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone = settings.TWILIO_FROM_PHONE

    if not (account_sid and auth_token and from_phone and to_phone and body):
        raise ValueError('Twilio SMS configuration incomplete or missing recipient/body')

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        'From': from_phone,
        'To': to_phone,
        'Body': body,
    }
    response = requests.post(url, auth=(account_sid, auth_token), data=data)
    response.raise_for_status()
    return response.json()


def send_bulk_twilio_sms(phone_numbers, body):
    results = []
    if not phone_numbers:
        return results

    for phone in phone_numbers:
        if not phone:
            continue
        results.append({
            'phone': phone,
            'result': send_twilio_sms(phone, body),
        })
    return results


def is_valid_paystack_signature(request):
    signature = request.headers.get('X-Paystack-Signature') or request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    if not signature:
        print(f'[WEBHOOK DEBUG] No signature header found. Headers: {list(request.headers.keys())}')
        return False

    secret = settings.PAYSTACK_WEBHOOK_SECRET or settings.PAYSTACK_SECRET_KEY
    if not secret:
        print('[WEBHOOK DEBUG] No webhook secret configured in settings')
        return False

    payload = request.body
    expected = hmac.new(secret.encode('utf-8'), payload, hashlib.sha512).hexdigest()
    is_valid = hmac.compare_digest(signature, expected)
    if not is_valid:
        print(f'[WEBHOOK DEBUG] Signature mismatch. Expected: {expected[:20]}... Got: {signature[:20]}...')
    return is_valid


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


def format_admin_order_sms(order, payment=None):
    template = getattr(settings, 'TWILIO_ORDER_ADMIN_SMS_TEMPLATE', '') or \
        'New order #{order_id} from {customer_name} for {total} {currency}. Call {phone} for delivery details.'
    return template.format(
        order_id=order.id,
        customer_name=f"{order.first_name} {order.last_name}",
        total=order.total,
        currency=settings.CURRENCY_SYMBOL,
        phone=order.phone or 'N/A',
        delivery_option=order.get_delivery_option_display(),
        site_url=settings.SITE_URL.rstrip('/') if hasattr(settings, 'SITE_URL') else '',
    )


def format_customer_order_sms(order, payment=None):
    template = getattr(settings, 'TWILIO_ORDER_CUSTOMER_SMS_TEMPLATE', '') or \
        'Thank you {customer_name}! Your order #{order_id} for {total} {currency} has been received. We will contact you shortly.'
    return template.format(
        order_id=order.id,
        customer_name=f"{order.first_name} {order.last_name}",
        total=order.total,
        currency=settings.CURRENCY_SYMBOL,
        delivery_option=order.get_delivery_option_display(),
        site_url=settings.SITE_URL.rstrip('/') if hasattr(settings, 'SITE_URL') else '',
    )


def send_sms_notification(order, payment=None, to_phone=None, body=None):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone = settings.TWILIO_FROM_PHONE
    to_phone = to_phone or settings.TWILIO_ADMIN_PHONE

    if not (account_sid and auth_token and from_phone and to_phone):
        return False

    if body is None:
        body = format_order_sms(order, payment)

    if isinstance(to_phone, (list, tuple)):
        results = []
        for phone in to_phone:
            if phone:
                results.append(send_twilio_sms(phone, body))
        return results

    return send_twilio_sms(to_phone, body)


def send_order_admin_sms(order, payment=None):
    admin_numbers = get_twilio_admin_numbers()
    if not admin_numbers:
        raise ValueError('No admin phone numbers configured for Twilio SMS')
    body = format_admin_order_sms(order, payment)
    return send_sms_notification(order, payment, to_phone=admin_numbers, body=body)


def send_order_customer_sms(order, payment=None):
    if not getattr(order, 'phone', None):
        raise ValueError('Order has no phone number for customer SMS')
    body = format_customer_order_sms(order, payment)
    return send_twilio_sms(order.phone, body)


def parse_paystack_amount(amount):
    if amount is None:
        return Decimal('0.00')
    return Decimal(amount) / Decimal('100')
