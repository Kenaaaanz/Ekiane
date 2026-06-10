from django.contrib import admin
from .models import Order, OrderItem


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
    inlines = [OrderItemInline]
