# analytics/forms.py
from django import forms
from .models import EOQParameters, DemandHistory

class EOQParametersForm(forms.ModelForm):
    class Meta:
        model = EOQParameters
        fields = [
            'product', 'annual_demand', 'order_cost', 'holding_cost',
            'stock_out_cost', 'safety_factor'
        ]
        widgets = {
            'annual_demand': forms.NumberInput(attrs={'step': '0.01'}),
            'order_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'holding_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'stock_out_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'safety_factor': forms.NumberInput(attrs={'step': '0.01'}),
        }

class DemandHistoryForm(forms.ModelForm):
    class Meta:
        model = DemandHistory
        fields = ['product', 'period_date', 'quantity_demanded', 'demand_type']
        widgets = {
            'period_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BulkDemandUploadForm(forms.Form):
    file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with columns: product_id, period_date (YYYY-MM-DD), quantity, type (actual/forecast)'
    )