from django import forms
from .models import Budget, BudgetItem, Transaction, Income, Expense
from apps.farms.models import Farm

class BudgetForm(forms.ModelForm):
    """Form for creating and editing farm budgets"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add empty choice to select fields
        self.fields['farm'].empty_label = "Select Farm"
        self.fields['status'].empty_label = "Select Status"
        
        # Make select fields required
        self.fields['farm'].required = True
        self.fields['status'].required = True
        
        # Filter farms by user
        if self.user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=self.user)
        
        # Add CSS classes and IDs for styling
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id': f'id_{field_name}'  # This will create id="id_farm" for the farm field
            })
    
    class Meta:
        model = Budget
        fields = [
            'farm', 'title', 'description', 'start_date', 'end_date',
            'total_planned_income', 'total_planned_expenses', 'status'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Budget Name'}),
            'total_planned_income': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_planned_expenses': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data

class BudgetItemForm(forms.ModelForm):
    """Form for creating and editing budget items"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add empty choice to select fields
        self.fields['item_type'].empty_label = "Select Type"
        
        # Make select fields required
        self.fields['item_type'].required = True
        
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    class Meta:
        model = BudgetItem
        fields = [
            'item_type', 'category', 'description', 'amount',
            'quantity', 'unit', 'price_per_unit'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }