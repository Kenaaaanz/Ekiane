from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext as _

from .models import Order, OrderItem
from payments.utils import send_bulk_twilio_sms


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['price', 'quantity']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'phone', 'total', 'paid', 'status', 'created_at']
    list_filter = ['paid', 'status', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone', 'exact_location']
    readonly_fields = ['total', 'created_at', 'updated_at']
    fieldsets = (
        ('Customer Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'user')
        }),
        ('Delivery Details', {
            'fields': ('delivery_option', 'exact_location', 'house_number', 'distance_km', 'delivery_fee')
        }),
        ('Order Status', {
            'fields': ('status', 'paid', 'total', 'created_at', 'updated_at')
        }),
    )
    change_list_template = 'admin/orders/order/change_list.html'
    inlines = [OrderItemInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-marketing-sms/', self.admin_site.admin_view(self.marketing_sms_view), name='orders_order_send_marketing_sms'),
        ]
        return custom_urls + urls

    def marketing_sms_view(self, request):
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['title'] = _('Send Marketing SMS')

        if request.method == 'POST':
            message = request.POST.get('message', '').strip()
            days = int(request.POST.get('days', '30') or 30)
            limit = int(request.POST.get('limit', '0') or 0)
            include_cancelled = request.POST.get('include_cancelled') == 'on'

            orders = Order.objects.filter(phone__isnull=False).exclude(phone='').filter(created_at__gte=self._get_cutoff(days))
            if not include_cancelled:
                orders = orders.exclude(status='cancelled')

            phone_list = list(orders.values_list('phone', flat=True))
            phone_numbers = [phone.strip() for phone in set(phone_list) if phone and phone.strip()]

            if limit > 0:
                phone_numbers = phone_numbers[:limit]

            if not message:
                messages.error(request, _('Please provide a message to send.'))
            elif not phone_numbers:
                messages.error(request, _('No customer phone numbers found for the selected criteria.'))
            else:
                try:
                    results = send_bulk_twilio_sms(phone_numbers, message)
                    messages.success(request, _('%(count)d marketing SMS messages sent successfully.') % {'count': len(results)})
                    context['sent_count'] = len(results)
                    context['phone_numbers'] = phone_numbers
                except Exception as e:
                    messages.error(request, _('Error sending marketing SMS: %(error)s') % {'error': str(e)})

        context['days'] = request.POST.get('days', '30')
        context['limit'] = request.POST.get('limit', '0')
        context['include_cancelled'] = request.POST.get('include_cancelled') == 'on'
        context['message'] = request.POST.get('message', '')
        return TemplateResponse(request, 'admin/orders/order/marketing_sms.html', context)

    def _get_cutoff(self, days):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - timedelta(days=days)

