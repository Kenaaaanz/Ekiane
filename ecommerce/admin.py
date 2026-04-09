from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from orders.models import Order, OrderItem
from store.models import Product, Category
from payments.models import Payment
from analytics.models import ProductBatch
from analytics.admin import ProductBatchAdmin
from analytics.signals import get_cached_analytics
from ecommerce.utils import CustomJSONEncoder
import json


class EkianeAdminSite(AdminSite):
    site_header = "Ekiane Admin"
    site_title = "Ekiane Luxury Organics"
    index_title = "Dashboard"
    site_url = "/"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.index), name='index'),
        ]
        return custom_urls + urls

    def get_app_list(self, request, app_label=None):
        """
        Add Analytics menu item to the admin sidebar
        """
        app_list = super().get_app_list(request, app_label)

        # Add Analytics app to the list
        analytics_app = {
            'name': 'Analytics',
            'app_label': 'analytics',
            'app_url': '/analytics/dashboard/',
            'has_module_perms': True,
            'models': [{
                'name': 'Analytics Dashboard',
                'object_name': 'AnalyticsDashboard',
                'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                'admin_url': '/analytics/dashboard/',
                'add_url': None,
                'view_only': True,
            }],
        }

        # Insert analytics app at the beginning
        app_list.insert(0, analytics_app)

        return app_list

    def index(self, request, extra_context=None):
        """
        Display the main admin index page with analytics dashboard.
        """
        # Get cached analytics data
        analytics_data = get_cached_analytics()

        context = {
            **self.each_context(request),
            'title': self.index_title,
            **analytics_data,
        }

        return TemplateResponse(request, 'admin/index.html', context)


# Create the custom admin site
admin_site = EkianeAdminSite(name='ekiane_admin')

# Register all models with the custom admin site
from store.admin import CategoryAdmin, ProductAdmin
from orders.admin import OrderAdmin
from payments.admin import PaymentAdmin

admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(ProductBatch, ProductBatchAdmin)