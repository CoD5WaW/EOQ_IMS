# warehouse/admin.py
from django.contrib import admin
from .models import Warehouse
from inventory.models import Inventory

class InventoryInline(admin.TabularInline):
    model = Inventory
    extra = 0
    raw_id_fields = ('product',)
    fields = ('product', 'quantity_on_hand', 'safety_stock', 'last_updated')
    readonly_fields = ('last_updated',)
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('warehouse_id', 'warehouse_name', 'location', 'storage_cost', 'active')
    list_filter = ('active', 'location')
    search_fields = ('warehouse_name', 'location', 'address')
    list_editable = ('active',)
    inlines = [InventoryInline]
    fieldsets = (
        (None, {'fields': ('warehouse_name', 'active')}),
        ('Location', {'fields': ('location', 'address')}),
        ('Cost Information', {'fields': ('storage_cost',)}),
    )