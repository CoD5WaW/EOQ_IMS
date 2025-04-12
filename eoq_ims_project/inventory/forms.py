# inventory/forms.py
from django import forms
from .models import Category, Product, Inventory, InventoryTransaction

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name', 'description', 'unit_cost', 'selling_price',
            'reorder_point', 'eoq', 'holding_cost_percentage', 'lead_time_days',
            'category', 'active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'holding_cost_percentage': forms.NumberInput(attrs={'step': '0.01'}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'warehouse', 'quantity_on_hand', 'safety_stock']

class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = [
            'product', 'warehouse', 'transaction_type', 'quantity',
            'transaction_date', 'reference_document', 'reference_id', 'notes'
        ]
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }