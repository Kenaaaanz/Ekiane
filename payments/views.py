import json
import requests
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from .models import Payment
from orders.models import Order


def initialize_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    reference = f"EKIANE-{order.id}-{order.created_at.strftime('%Y%m%d%H%M%S')}"
    callback_url = request.build_absolute_uri(reverse('payments:verify_payment'))
    amount_kobo = int(order.total * Decimal('100'))

    payload = {
        'email': order.email,
        'amount': amount_kobo,
        'reference': reference,
        'currency': 'KES',
        'callback_url': callback_url,
        'subaccount': settings.PAYSTACK_SUBACCOUNT_CODE,
        'transaction_charge': int(amount_kobo * settings.PLATFORM_FEE_PERCENT / 100),
        'metadata': {
            'order_id': order.id,
        },
    }

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(payload))
    data = response.json()
    if data.get('status') and data.get('data'):
        Payment.objects.update_or_create(
            order=order,
            defaults={
                'reference': reference,
                'amount': order.total,
                'status': 'initialized',
            }
        )
        authorization_url = data['data'].get('authorization_url')
        return redirect(authorization_url)

    return render(request, 'payments/payment_error.html', {'error': data.get('message', 'Unable to initiate payment')})


def verify_payment(request):
    reference = request.GET.get('reference')
    if not reference:
        return render(request, 'payments/payment_error.html', {'error': 'Missing payment reference.'})

    headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
    response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
    data = response.json()

    if not data.get('status'):
        return render(request, 'payments/payment_error.html', {'error': data.get('message', 'Verification failed')})

    payment_data = data['data']
    metadata = payment_data.get('metadata') or {}
    order_id = metadata.get('order_id')

    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        payment = None

    if not payment and order_id:
        order = get_object_or_404(Order, pk=order_id)
        payment = Payment.objects.create(
            order=order,
            reference=reference,
            amount=order.total,
            status='initialized',
        )

    if payment_data['status'] == 'success' and payment:
        order = payment.order
        order.paid = True
        order.status = 'paid'
        order.save()  # Save order FIRST so signal can access order.paid = True
        
        payment.status = 'success'
        payment.verified_at = timezone.now()
        payment.save()  # This triggers the signal after order.paid is True

        request.session['order_id'] = order.id
        return redirect('orders:order_success')

    if payment:
        payment.status = 'failed'
        payment.save()

    return render(request, 'payments/payment_error.html', {'error': 'Payment was not successful.'})
