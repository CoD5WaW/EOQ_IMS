# analytics/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import EOQParameters, DemandHistory

@admin.register(EOQParameters)
class EOQParametersAdmin(admin.ModelAdmin):
    list_display = ('parameter_id', 'product_link', 'annual_demand', 'order_cost', 'holding_cost', 'last_calculated', 'calculate_eoq_button')
    list_filter = ('last_calculated',)
    search_fields = ('product__product_name',)
    readonly_fields = ('last_calculated', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('product',)}),
        ('EOQ Parameters', {'fields': ('annual_demand', 'order_cost', 'holding_cost')}),
        ('Advanced', {'fields': ('stock_out_cost', 'safety_factor')}),
        ('Timestamps', {'fields': ('last_calculated', 'created_at', 'updated_at')}),
    )
    
    def product_link(self, obj):
        url = reverse('admin:inventory_product_change', args=[obj.product.product_id])
        return format_html('<a href="{}">{}</a>', url, obj.product.product_name)
    product_link.short_description = 'Product'
    
    def calculate_eoq_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Calculate EOQ</a>',
            reverse('admin:calculate_eoq', args=[obj.parameter_id])
        )
    calculate_eoq_button.short_description = 'Action'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/calculate_eoq/',
                self.admin_site.admin_view(self.calculate_eoq_view),
                name='calculate_eoq',
            ),
        ]
        return custom_urls + urls
    
    def calculate_eoq_view(self, request, object_id):
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        from django.urls import reverse
        
        params = self.get_object(request, object_id)
        eoq = params.calculate_eoq()
        
        messages.success(request, f"EOQ calculated successfully. New EOQ value: {eoq:.2f}")
        return HttpResponseRedirect(reverse('admin:analytics_eoqparameters_change', args=[object_id]))

@admin.register(DemandHistory)
class DemandHistoryAdmin(admin.ModelAdmin):
    list_display = ('history_id', 'product', 'period_date', 'quantity_demanded', 'demand_type', 'created_at')
    list_filter = ('demand_type', 'period_date')
    search_fields = ('product__product_name',)
    date_hierarchy = 'period_date'
    raw_id_fields = ('product',)