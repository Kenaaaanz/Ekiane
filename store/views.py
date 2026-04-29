from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from website_settings.models import AboutPage


def get_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        items.append({
            'product': product,
            'quantity': quantity,
            'item_total': product.price * quantity,
        })
        total += product.price * quantity
    return {'items': items, 'total': total}


def home(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})


def cart_detail(request):
    cart = get_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, available=True)
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    cart[str(product.id)] = cart.get(str(product.id), 0) + quantity
    request.session['cart'] = cart
    return redirect('store:cart_detail')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('store:cart_detail')


def about(request):
    about_page, created = AboutPage.objects.get_or_create(id=1)
    return render(request, 'store/about.html', {'about_page': about_page})
