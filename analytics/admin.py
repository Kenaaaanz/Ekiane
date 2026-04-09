from django.contrib import admin
from .models import ProductBatch, BatchMaterial


class BatchMaterialInline(admin.TabularInline):
    model = BatchMaterial
    extra = 1
    readonly_fields = ['total_cost']
    fields = ['name', 'unit_cost', 'quantity', 'total_cost']

    def total_cost(self, obj):
        if obj is None:
            return None
        return obj.total_cost
    total_cost.short_description = 'Total Cost'


class ProductBatchAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'batch_date',
        'quantity_produced',
        'quantity_sold',
        'status',
        'material_cost',
        'total_revenue',
        'total_profit',
        'days_open',
    ]
    list_filter = ['product', 'batch_date', 'status']
    search_fields = ['product__name', 'notes']
    date_hierarchy = 'batch_date'
    inlines = [BatchMaterialInline]
    readonly_fields = [
        'material_cost',
        'cost_per_unit',
        'product_cost',
        'cost_variance',
        'profit_margin',
        'quantity_sold',
        'status',
        'open_date',
        'close_date',
        'quantity_remaining',
        'days_open',
        'total_revenue',
        'total_profit',
        'profit_per_day',
        'profit_per_month',
        'time_to_sell_out',
        'sell_through_rate',
    ]
    fieldsets = (
        (None, {
            'fields': ('product', 'batch_date', 'quantity_produced', 'notes')
        }),
        ('Status', {
            'fields': ('status', 'open_date', 'close_date', 'quantity_sold', 'quantity_remaining')
        }),
        ('Performance', {
            'fields': (
                'material_cost',
                'cost_per_unit',
                'product_cost',
                'cost_variance',
                'profit_margin',
                'total_revenue',
                'total_profit',
                'profit_per_day',
                'profit_per_month',
                'days_open',
                'time_to_sell_out',
                'sell_through_rate',
            )
        }),
    )

    def material_cost(self, obj):
        return obj.material_cost()

    def cost_per_unit(self, obj):
        return obj.cost_per_unit()

    def product_cost(self, obj):
        return obj.product_cost()

    def cost_variance(self, obj):
        return obj.cost_variance()

    def profit_margin(self, obj):
        return f"{obj.profit_margin():.2f}%"

    material_cost.short_description = 'Material Cost'
    cost_per_unit.short_description = 'Cost / Unit'
    product_cost.short_description = 'Product Cost'
    cost_variance.short_description = 'Cost Variance'
    profit_margin.short_description = 'Profit Margin'
