# inventory/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage, Inventory, InventoryTransaction

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_featured', 'sort_order')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'category', 'unit_cost', 'selling_price', 'reorder_point', 'active')
    list_filter = ('active', 'category', 'created_at')
    search_fields = ('product_name', 'description')
    date_hierarchy = 'created_at'
    list_editable = ('active',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {'fields': ('product_name', 'description', 'category', 'active')}),
        ('Images', {'fields': ('main_image',)}),
        ('Pricing', {'fields': ('unit_cost', 'selling_price')}),
        ('Inventory Control', {'fields': ('reorder_point', 'eoq', 'holding_cost_percentage', 'lead_time_days')}),
        ('System Fields', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'alt_text', 'is_featured', 'sort_order', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('product__product_name', 'alt_text')
    raw_id_fields = ('product',)
    list_editable = ('is_featured', 'sort_order')
    readonly_fields = ('created_at',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventory_id', 'product', 'warehouse', 'quantity_on_hand', 'safety_stock', 'last_updated')
    list_filter = ('warehouse', 'last_updated')
    search_fields = ('product__product_name', 'warehouse__warehouse_name')
    raw_id_fields = ('product', 'warehouse')
    readonly_fields = ('last_updated',)

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'product', 'warehouse', 'transaction_type', 'quantity', 'transaction_date')
    list_filter = ('transaction_type', 'warehouse', 'transaction_date')
    search_fields = ('product__product_name', 'notes', 'reference_document')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('product', 'warehouse', 'transaction_type', 'quantity')}),
        ('Details', {'fields': ('transaction_date', 'reference_document', 'reference_id', 'notes')}),
        ('System Fields', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )