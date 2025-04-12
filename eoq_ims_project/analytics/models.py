# analytics/models.py
from django.db import models
from django.utils import timezone
from inventory.models import Product

class EOQParameters(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='eoq_parameters')
    annual_demand = models.DecimalField(max_digits=12, decimal_places=2)
    order_cost = models.DecimalField(max_digits=10, decimal_places=2)
    holding_cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock_out_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    safety_factor = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    last_calculated = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"EOQ Parameters for {self.product.product_name}"

    def calculate_eoq(self):
        """Calculate the Economic Order Quantity using the standard EOQ formula"""
        import math
        eoq = math.sqrt((2 * float(self.annual_demand) * float(self.order_cost)) / float(self.holding_cost))
        self.product.eoq = eoq
        self.product.save()
        self.last_calculated = timezone.now()
        self.save()
        return eoq

class DemandHistory(models.Model):
    DEMAND_TYPES = (
        ('actual', 'Actual'),
        ('forecast', 'Forecast'),
    )
    
    history_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='demand_history')
    period_date = models.DateField()
    quantity_demanded = models.IntegerField()
    demand_type = models.CharField(max_length=50, choices=DEMAND_TYPES, default='actual')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.period_date} - {self.quantity_demanded}"

    class Meta:
        ordering = ['-period_date']
        verbose_name_plural = 'Demand Histories'