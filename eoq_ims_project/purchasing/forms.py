# purchasing/forms.py
from django import forms
from .models import Supplier, PurchaseOrder, POItem

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'supplier_name', 'contact_person', 'phone', 'email',
            'address', 'order_cost', 'lead_time_days', 'active'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'order_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'expected_delivery', 'po_status']
        widgets = {
            'order_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expected_delivery': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class POItemForm(forms.ModelForm):
    class Meta:
        model = POItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

# Form for handling multiple PO items at once
class POItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        
        # Validate that at least one item is added
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False) for form in self.forms):
            raise forms.ValidationError("At least one item must be added to the purchase order.")