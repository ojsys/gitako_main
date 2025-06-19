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
        self.fields['total_planned_income'].required = False
        self.fields['total_planned_expenses'].required = False
        self.fields['status'].required = False
        
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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter Budget Name'}),
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
        
        # Make required fields explicit
        self.fields['item_type'].required = True
        self.fields['category'].required = True
        self.fields['description'].required = True
        self.fields['amount'].required = True
        self.fields['actual_amount'].required = False
        self.fields['variance'].required = False
        self.fields['variance'].widget.attrs['readonly'] = True # Add this line
        
        # Optional fields
        self.fields['quantity'].required = False
        self.fields['unit'].required = False
        self.fields['price_per_unit'].required = False
        
        # Add CSS classes and IDs for styling
        for field_name, field in self.fields.items():
            css_class = 'form-control'
            field.widget.attrs.update({
                'class': css_class,
                'id': f'id_{field_name}'
            })
        
        # Add placeholders for better UX
        self.fields['category'].widget.attrs['placeholder'] = 'e.g., Seeds, Fertilizer, Labor'
        self.fields['description'].widget.attrs['placeholder'] = 'Brief description of the item'
        self.fields['amount'].widget.attrs['placeholder'] = '0.00'
        self.fields['actual_amount'].widget.attrs['placeholder'] = '0.00'
        self.fields['variance'].widget.attrs['placeholder'] = '0.00'
        self.fields['quantity'].widget.attrs['placeholder'] = 'Optional quantity'
        self.fields['unit'].widget.attrs['placeholder'] = 'e.g., kg, bags, hours'
        self.fields['price_per_unit'].widget.attrs['placeholder'] = 'Price per unit'
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        price_per_unit = cleaned_data.get('price_per_unit')
        amount = cleaned_data.get('amount')
        actual_amount = cleaned_data.get('actual_amount')
        # variance = cleaned_data.get('variance') # We will calculate this, so no need to get from cleaned_data
    
        # Calculate variance if amount and actual_amount are present
        if amount is not None and actual_amount is not None:
            cleaned_data['variance'] = float(amount) - float(actual_amount)
        else:
            cleaned_data['variance'] = None # Or 0.00 if you prefer
        
        # If quantity and price_per_unit are provided, validate amount calculation
        if quantity is not None and price_per_unit is not None and amount:
            calculated_amount = quantity * price_per_unit
            if abs(float(amount) - float(calculated_amount)) > 0.01:  # Allow small rounding differences
                self.add_error('amount', 
                    f'Amount should equal quantity × price per unit (₦{calculated_amount:.2f})')
        
        return cleaned_data
    
    class Meta:
        model = BudgetItem
        fields = [
            'item_type', 'category', 'description', 'amount', 'actual_amount', 'variance',
            'quantity', 'unit', 'price_per_unit'
        ]
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0'
            }),
            'actual_amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0'
            }),
            'variance': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0'
            }),

            'quantity': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0'
            }),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0'
            }),
        }
        
        labels = {
            'item_type': 'Type',
            'category': 'Category',
            'description': 'Description',
            'amount': 'Amount (₦)',
            'actual_amount': 'Actual Amount (₦)',
            'variance': 'Variance (₦)',
            'quantity': 'Quantity',
            'unit': 'Unit',
            'price_per_unit': 'Price per Unit (₦)',
        }
        
        help_texts = {
            'item_type': 'Select whether this is an income or expense item',
            'category': 'Category of the budget item (e.g., Seeds, Labor, Sales)',
            'description': 'Brief description of what this item is for',
            'amount': 'Amount for this budget item',
            'actual_amount': 'Actual amount for this budget item',
            'variance': 'Variance between amount and actual amount',
            'quantity': 'Optional: How many units (leave blank if not applicable)',
            'unit': 'Optional: Unit of measurement (e.g., kg, bags, hours)',
            'price_per_unit': 'Optional: Price per individual unit',
        }