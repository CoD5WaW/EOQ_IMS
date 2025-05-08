# inventory/forms.py
from django import forms
from .models import Category, Product, ProductImage, Inventory, InventoryTransaction

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# inventory/forms.py - revised portion
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name', 'description', 'main_image', 'unit_cost', 'selling_price',
            'reorder_point', 'eoq', 'holding_cost_percentage', 'lead_time_days',
            'category', 'active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'holding_cost_percentage': forms.NumberInput(attrs={'step': '0.01'}),
        }

# Remove the ProductImageFormSet and related code since we won't use it anymore
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_featured', 'sort_order']

class ProductImageFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        featured_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_featured', False):
                    featured_count += 1
        
        if featured_count > 1:
            raise forms.ValidationError("Only one image can be set as featured.")

ProductImageInlineFormSet = forms.inlineformset_factory(
    Product, ProductImage, form=ProductImageForm, formset=ProductImageFormSet,
    extra=3, can_delete=True
)

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