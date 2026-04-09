from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.db.models import Sum, Q
from payments.models import Payment
from orders.models import Order, OrderItem
from store.models import Product, Category
from analytics.models import ProductBatch
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import json
from ecommerce.utils import CustomJSONEncoder


@receiver(post_save, sender=Payment)
def update_analytics_on_payment_success(sender, instance, created, **kwargs):
    """Update analytics and product batches when payment status changes to success"""
    if instance.status == 'success':
        # Update product batches with sold quantities
        order = instance.order
        update_batches_from_order(order)
        
        # Clear existing cache
        cache.delete('analytics_dashboard_data')

        # Recompute and cache analytics data
        _compute_and_cache_analytics()


@receiver(post_save, sender=OrderItem)
def track_order_item_creation(sender, instance, created, **kwargs):
    """Track when order items are created - batches will be updated when order is paid"""
    pass  # Batch updates happen on payment success, not on order item creation


def update_batches_from_order(order):
    """Update product batch quantities when order is paid"""
    if not order.paid:
        return
    
    # Get all items in this order
    order_items = order.items.all()
    
    for item in order_items:
        product = item.product
        quantity_sold = item.quantity
        
        # Find the earliest open batch for this product
        open_batch = ProductBatch.objects.filter(
            product=product,
            status='open'
        ).order_by('batch_date').first()
        
        if open_batch:
            # Update the batch with sold quantity
            open_batch.sell_quantity(quantity_sold)
        
        # Decrease product stock immediately
        product.stock = max(0, product.stock - quantity_sold)
        product.save()


def _compute_and_cache_analytics():
    """Compute and cache all analytics data - LIVE DATA"""
    # Use fresh data each time - no cached query results
    orders = Order.objects.filter(paid=True)
    total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
    total_cost = sum(order.get_cost() for order in orders)
    total_profit = sum(order.get_profit() for order in orders)
    total_platform_fee = sum(order.get_platform_fee() for order in orders)
    order_count = orders.count()

    # Top products - LIVE
    top_products = Product.objects.annotate(
        sold_quantity=Sum('orderitem__quantity', filter=Q(orderitem__order__paid=True))
    ).order_by('-sold_quantity')[:5]

    # Revenue over last 30 days - LIVE
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_revenue = {}
    daily_orders = {}
    for order in orders.filter(created_at__gte=thirty_days_ago):
        date_key = order.created_at.strftime('%Y-%m-%d')
        daily_revenue[date_key] = daily_revenue.get(date_key, 0) + float(order.total)
        daily_orders[date_key] = daily_orders.get(date_key, 0) + 1

    # Category breakdown - LIVE
    category_sales = {}
    for category in Category.objects.all():
        category_items = OrderItem.objects.filter(
            product__category=category,
            order__paid=True
        )
        category_sales[category.name] = {
            'quantity': category_items.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'revenue': sum(item.get_cost() for item in category_items)
        }

    # Profit vs Cost comparison - LIVE
    profit_data = {
        'profit': int(total_profit),
        'cost': int(total_cost),
        'revenue': int(total_revenue),
        'fees': int(total_platform_fee)
    }

    # Top categories by revenue - LIVE
    top_categories = sorted(
        category_sales.items(),
        key=lambda x: x[1]['revenue'],
        reverse=True
    )[:5]

    # Product batch performance - LIVE DATA
    batch_queryset = ProductBatch.objects.select_related('product').order_by('-batch_date')[:10]
    batch_data = []
    batch_labels = []
    batch_costs = []
    batch_target_costs = []
    batch_margins = []
    batch_variances = []
    batch_profits = []
    batch_days_open = []

    for batch in batch_queryset:
        batch_data.append({
            'id': batch.id,
            'batch_date': batch.batch_date.isoformat() if batch.batch_date else None,
            'quantity_produced': batch.quantity_produced,
            'quantity_sold': batch.quantity_sold,
            'quantity_remaining': batch.quantity_remaining,
            'status': batch.status,
            'open_date': batch.open_date.isoformat() if batch.open_date else None,
            'close_date': batch.close_date.isoformat() if batch.close_date else None,
            'notes': batch.notes,
            'product_name': batch.product.name,
            'cost_per_unit': float(batch.cost_per_unit()),
            'product_cost': float(batch.product_cost()),
            'cost_variance': float(batch.cost_variance()),
            'profit_margin': float(batch.profit_margin()),
            'total_revenue': float(batch.total_revenue()),
            'total_profit': float(batch.total_profit()),
            'profit_per_day': float(batch.profit_per_day()),
            'profit_per_month': float(batch.profit_per_month()),
            'days_open': batch.days_open,
            'time_to_sell_out': batch.time_to_sell_out(),
            'sell_through_rate': float(batch.sell_through_rate),
        })
        batch_labels.append(f"{batch.product.name} {batch.batch_date}")
        batch_costs.append(float(batch.cost_per_unit()))
        batch_target_costs.append(float(batch.product_cost()))
        batch_margins.append(float(batch.profit_margin()))
        batch_variances.append(float(batch.cost_variance()))
        batch_profits.append(float(batch.total_profit()))
        batch_days_open.append(batch.days_open)

    # Prepare analytics data for caching
    analytics_data = {
        'total_revenue': int(total_revenue),
        'total_cost': int(total_cost),
        'total_profit': int(total_profit),
        'total_platform_fee': int(total_platform_fee),
        'order_count': order_count,
        'top_products': list(top_products.values('name', 'sold_quantity')),
        'daily_revenue_json': json.dumps(daily_revenue, cls=CustomJSONEncoder),
        'daily_orders_json': json.dumps(daily_orders, cls=CustomJSONEncoder),
        'profit_data_json': json.dumps(profit_data, cls=CustomJSONEncoder),
        'category_sales': top_categories,
        'category_sales_json': json.dumps({k: v['revenue'] for k, v in top_categories}, cls=CustomJSONEncoder),
        'category_units_json': json.dumps({k: v['quantity'] for k, v in top_categories}, cls=CustomJSONEncoder),
        'product_performance_batches': batch_data,
        'batch_labels_json': json.dumps(batch_labels, cls=CustomJSONEncoder),
        'batch_costs_json': json.dumps(batch_costs, cls=CustomJSONEncoder),
        'batch_target_costs_json': json.dumps(batch_target_costs, cls=CustomJSONEncoder),
        'batch_margins_json': json.dumps(batch_margins, cls=CustomJSONEncoder),
        'batch_variances_json': json.dumps(batch_variances, cls=CustomJSONEncoder),
        'batch_profits_json': json.dumps(batch_profits, cls=CustomJSONEncoder),
        'batch_days_open_json': json.dumps(batch_days_open, cls=CustomJSONEncoder),
        'currency_symbol': 'KES',
        'last_updated': timezone.now().isoformat(),
    }

    # Cache for 1 hour (3600 seconds) - shorter for live updates
    cache.set('analytics_dashboard_data', analytics_data, 3600)


def get_cached_analytics():
    """Get analytics data from cache, compute if not available"""
    analytics_data = cache.get('analytics_dashboard_data')
    if analytics_data is None:
        _compute_and_cache_analytics()
        analytics_data = cache.get('analytics_dashboard_data')
    return analytics_data