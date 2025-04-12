# purchasing/models.py
from django.db import models
from django.utils import timezone
from inventory.models import Product

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    order_cost = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.supplier_name

    class Meta:
        ordering = ['supplier_name']

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )
    
    po_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.RESTRICT)
    order_date = models.DateTimeField(default=timezone.now)
    expected_delivery = models.DateTimeField(blank=True, null=True)
    actual_delivery = models.DateTimeField(blank=True, null=True)
    po_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO-{self.po_id}-{self.supplier.supplier_name}"

    class Meta:
        ordering = ['-order_date']

class POItem(models.Model):
    po_item_id = models.AutoField(primary_key=True)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} units"

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update PO total
        self.po.total_cost = sum(item.line_total for item in self.po.items.all())
        self.po.save()
