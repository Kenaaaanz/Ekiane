from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from orders.models import Order, OrderItem
from store.models import Product, Category
from analytics.models import ProductBatch
from analytics.signals import get_cached_analytics
from ecommerce.utils import CustomJSONEncoder
import json


@staff_member_required
def dashboard(request):
    # Get cached analytics data
    analytics_data = get_cached_analytics()

    return render(request, 'analytics/dashboard.html', analytics_data)


@staff_member_required
def productbatch_list(request):
    """Display all product batches with live performance metrics"""
    batches = ProductBatch.objects.select_related('product').order_by('-batch_date')
    
    batch_data = []
    for batch in batches:
        batch_data.append({
            'id': batch.id,
            'batch_date': batch.batch_date,
            'product_name': batch.product.name,
            'quantity_produced': batch.quantity_produced,
            'quantity_sold': batch.quantity_sold,
            'quantity_remaining': batch.quantity_remaining,
            'status': batch.status,
            'days_open': batch.days_open,
            'cost_per_unit': float(batch.cost_per_unit()),
            'product_cost': float(batch.product_cost()),
            'cost_variance': float(batch.cost_variance()),
            'profit_margin': float(batch.profit_margin()),
            'total_revenue': float(batch.total_revenue()),
            'total_profit': float(batch.total_profit()),
            'profit_per_day': float(batch.profit_per_day()),
            'profit_per_month': float(batch.profit_per_month()),
            'time_to_sell_out': batch.time_to_sell_out(),
            'sell_through_rate': float(batch.sell_through_rate),
            'material_cost': float(batch.material_cost()),
        })
    
    context = {
        'product_batches': batches,
        'batch_data': json.dumps(batch_data, cls=CustomJSONEncoder),
        'total_batches': batches.count(),
        'open_batches': batches.filter(status='open').count(),
        'closed_batches': batches.filter(status='closed').count(),
    }
    
    return render(request, 'analytics/productbatch.html', context)


@staff_member_required
def productbatch_api(request):
    """API endpoint for live product batch data with JSON response"""
    batches = ProductBatch.objects.select_related('product').order_by('-batch_date')
    
    batch_list = []
    for batch in batches:
        batch_list.append({
            'id': batch.id,
            'batch_date': str(batch.batch_date),
            'product_name': batch.product.name,
            'quantity_produced': batch.quantity_produced,
            'quantity_sold': batch.quantity_sold,
            'quantity_remaining': batch.quantity_remaining,
            'status': batch.status,
            'days_open': batch.days_open,
            'cost_per_unit': float(batch.cost_per_unit()),
            'profit_margin': float(batch.profit_margin()),
            'total_revenue': float(batch.total_revenue()),
            'total_profit': float(batch.total_profit()),
            'profit_per_day': float(batch.profit_per_day()),
            'time_to_sell_out': batch.time_to_sell_out(),
            'sell_through_rate': float(batch.sell_through_rate),
        })
    
    stats = {
        'total_batches': batches.count(),
        'open_batches': batches.filter(status='open').count(),
        'closed_batches': batches.filter(status='closed').count(),
        'total_produced': batches.aggregate(Sum('quantity_produced'))['quantity_produced__sum'] or 0,
        'total_sold': batches.aggregate(Sum('quantity_sold'))['quantity_sold__sum'] or 0,
        'total_profit': sum(b.total_profit() for b in batches),
        'average_sell_through_rate': sum(b.sell_through_rate for b in batches) / batches.count() if batches.count() > 0 else 0,
        'timestamp': timezone.now().isoformat(),
    }
    
    return JsonResponse({
        'success': True,
        'data': batch_list,
        'stats': stats,
    })


@staff_member_required
def analytics_api(request):
    """API endpoint for live analytics dashboard data"""
    analytics_data = get_cached_analytics()
    
    # Convert to JSON-safe format
    response_data = {
        'total_revenue': analytics_data.get('total_revenue', 0),
        'total_cost': analytics_data.get('total_cost', 0),
        'total_profit': analytics_data.get('total_profit', 0),
        'total_platform_fee': analytics_data.get('total_platform_fee', 0),
        'order_count': analytics_data.get('order_count', 0),
        'profit_data': json.loads(analytics_data.get('profit_data_json', '{}')),
        'timestamp': timezone.now().isoformat(),
    }
    
    return JsonResponse({
        'success': True,
        'data': response_data,
    })
