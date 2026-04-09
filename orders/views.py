from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Order, OrderItem
from store.models import Product


def get_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        item_total = product.price * quantity
        total += item_total
        items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total,
        })
    return {'items': items, 'total': total}


def checkout(request):
    cart = get_cart(request)
    if not cart['items']:
        return redirect('store:home')

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')

        order = Order.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            address=address,
            city=city,
            postal_code=postal_code,
            total=cart['total'],
        )

        for item in cart['items']:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['product'].price,
                quantity=item['quantity'],
            )

        request.session['order_id'] = order.id
        request.session['cart'] = {}
        return redirect('payments:initialize_payment', order_id=order.id)

    return render(request, 'orders/checkout.html', {'cart': cart})


def order_success(request):
    order_id = request.session.get('order_id')
    order = None
    if order_id:
        order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/order_success.html', {'order': order})
