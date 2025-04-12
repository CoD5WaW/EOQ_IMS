# warehouse/forms.py
from django import forms
from .models import Warehouse

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['warehouse_name', 'location', 'address', 'storage_cost', 'active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'storage_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }