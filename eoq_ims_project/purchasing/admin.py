# purchasing/admin.py
from django.contrib import admin
from .models import Supplier, PurchaseOrder, POItem

class POItemInline(admin.TabularInline):
    model = POItem
    extra = 1
    raw_id_fields = ('product',)
    fields = ('product', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_id', 'supplier_name', 'contact_person', 'email', 'phone', 'lead_time_days', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('supplier_name', 'contact_person', 'email', 'phone')
    date_hierarchy = 'created_at'
    list_editable = ('active',)
    fieldsets = (
        (None, {'fields': ('supplier_name', 'active')}),
        ('Contact Information', {'fields': ('contact_person', 'phone', 'email', 'address')}),
        ('Supply Details', {'fields': ('order_cost', 'lead_time_days')}),
    )

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_id', 'supplier', 'order_date', 'expected_delivery', 'po_status', 'total_cost')
    list_filter = ('po_status', 'order_date', 'expected_delivery')
    search_fields = ('supplier__supplier_name', 'po_id')
    date_hierarchy = 'order_date'
    readonly_fields = ('total_cost', 'created_at', 'updated_at')
    inlines = [POItemInline]
    fieldsets = (
        (None, {'fields': ('supplier', 'po_status')}),
        ('Dates', {'fields': ('order_date', 'expected_delivery', 'actual_delivery')}),
        ('Details', {'fields': ('total_cost', 'created_at', 'updated_at')}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.po_status in ['received', 'cancelled']:
            return self.readonly_fields + ('supplier', 'order_date', 'po_status')
        return self.readonly_fields