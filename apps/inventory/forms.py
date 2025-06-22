from django import forms
from django.contrib.auth.models import User
from .models import (
    InventoryItem, Equipment, FarmInput, InventoryTransaction, MaintenanceRecord
)
from apps.farms.models import Farm
from apps.activities.models import Activity


class InventoryItemForm(forms.ModelForm):
    """Form for creating and editing inventory items"""
    
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'item_type', 'description', 'quantity', 'unit',
            'status', 'storage_location', 'acquisition_date', 'farm'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name'
            }),
            'item_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the item'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., kg, pieces, liters'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'storage_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where is this item stored?'
            }),
            'acquisition_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'farm': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=self.user)
            self.fields['farm'].empty_label = "Select a farm (optional)"


class EquipmentForm(forms.ModelForm):
    """Form for equipment-specific details"""
    
    class Meta:
        model = Equipment
        fields = [
            'brand', 'model', 'serial_number', 'year', 'power_source',
            'horsepower', 'capacity', 'purchase_price', 'current_value',
            'maintenance_interval_days'
        ]
        widgets = {
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Equipment brand'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Model number/name'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Serial number'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2030'
            }),
            'power_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Diesel, Electric, Manual'
            }),
            'horsepower': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'capacity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 50 liters, 2 tons'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'current_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'maintenance_interval_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Days between maintenance'
            })
        }


class FarmInputForm(forms.ModelForm):
    """Form for farm input-specific details"""
    
    class Meta:
        model = FarmInput
        fields = [
            'input_category', 'brand', 'manufacturer', 'batch_number',
            'production_date', 'expiry_date', 'purchase_date', 'purchase_price',
            'supplier', 'application_rate', 'target_crops'
        ]
        widgets = {
            'input_category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Fertilizer, Pesticide, Seeds'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brand name'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manufacturer'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Batch/Lot number'
            }),
            'production_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier name'
            }),
            'application_rate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2kg per hectare'
            }),
            'target_crops': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Crops this input is for'
            })
        }


class InventoryTransactionForm(forms.ModelForm):
    """Form for recording inventory transactions"""
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'transaction_type', 'quantity', 'date', 'related_activity',
            'related_farm', 'unit_price', 'notes'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'related_activity': forms.Select(attrs={
                'class': 'form-control'
            }),
            'related_farm': forms.Select(attrs={
                'class': 'form-control'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this transaction'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['related_activity'].queryset = Activity.objects.filter(
                field__farm__owner=self.user
            )
            self.fields['related_farm'].queryset = Farm.objects.filter(owner=self.user)
            
            # Make fields optional
            self.fields['related_activity'].empty_label = "Select activity (optional)"
            self.fields['related_farm'].empty_label = "Select farm (optional)"


class MaintenanceRecordForm(forms.ModelForm):
    """Form for recording equipment maintenance"""
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'maintenance_date', 'maintenance_type', 'description', 'cost',
            'parts_replaced', 'service_provider', 'technician_name',
            'next_maintenance_date'
        ]
        widgets = {
            'maintenance_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'maintenance_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Routine, Repair, Overhaul'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the maintenance performed'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'parts_replaced': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List parts that were replaced'
            }),
            'service_provider': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company or person who did the work'
            }),
            'technician_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Technician name'
            }),
            'next_maintenance_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }


class QuickTransactionForm(forms.Form):
    """Quick form for simple inventory transactions"""
    
    TRANSACTION_CHOICES = [
        ('usage', 'Usage'),
        ('adjustment', 'Adjustment'),
        ('disposal', 'Disposal')
    ]
    
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quick note (optional)'
        })
    )


class InventorySearchForm(forms.Form):
    """Form for searching inventory"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search inventory...'
        })
    )
    item_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(InventoryItem.ItemType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + InventoryItem.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    low_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    expiring_soon = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )