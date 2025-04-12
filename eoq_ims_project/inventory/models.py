# inventory/models.py
from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_point = models.IntegerField()
    eoq = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    holding_cost_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    lead_time_days = models.IntegerField(blank=True, null=True)
    # Replace the CharField with a ForeignKey to Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    class Meta:
        ordering = ['product_name']

class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.CASCADE, related_name='inventories')
    quantity_on_hand = models.IntegerField(default=0)
    safety_stock = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.product_name} at {self.warehouse.warehouse_name}"

    class Meta:
        unique_together = ('product', 'warehouse')
        verbose_name_plural = 'Inventories'

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('receipt', 'Receipt'),
        ('issue', 'Issue'),
        ('adjustment_positive', 'Positive Adjustment'),
        ('adjustment_negative', 'Negative Adjustment'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    )
    
    transaction_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.RESTRICT)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    transaction_date = models.DateTimeField(default=timezone.now)
    reference_document = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.product_name} - {self.quantity}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.update_inventory()

    def update_inventory(self):
        try:
            inventory = Inventory.objects.get(product=self.product, warehouse=self.warehouse)
        except Inventory.DoesNotExist:
            inventory = Inventory(product=self.product, warehouse=self.warehouse, quantity_on_hand=0, safety_stock=0)
        
        if self.transaction_type in ('receipt', 'adjustment_positive', 'transfer_in'):
            inventory.quantity_on_hand += self.quantity
        elif self.transaction_type in ('issue', 'adjustment_negative', 'transfer_out'):
            inventory.quantity_on_hand -= self.quantity
        
        inventory.save()
