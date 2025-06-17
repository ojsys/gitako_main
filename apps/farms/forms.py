# Create this as forms.py in your farms app

from django import forms
from django.core.exceptions import ValidationError
from .models import Farm, FarmSection, Crop, CropVariety, CropCycle 
#Disease, Pest, SoilTest, WaterSource, Fertilizer, WeatherData
from django.utils import timezone
from datetime import date, timedelta

class FarmSectionForm(forms.ModelForm):
    """Form for creating and editing farm sections/fields"""
    
    class Meta:
        model = FarmSection
        fields = ['farm', 'name', 'description', 'size', 'crop_type', 'livestock_type', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter field name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter field description (optional)'
            }),
            'size': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Size in acres'
            }),
            'crop_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary crop type (optional)'
            }),
            'livestock_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Livestock type (optional)'
            }),
            'farm': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit farm choices to user's farms
        if self.user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=self.user, is_active=True)
        
        self.fields['farm'].empty_label = "Select a Farm"
        
        # Add labels and help text
        self.fields['name'].label = 'Field Name'
        self.fields['size'].label = 'Field Size (acres)'
        self.fields['size'].help_text = 'Enter the size of this field in acres'
        self.fields['crop_type'].label = 'Primary Crop Type'
        self.fields['crop_type'].help_text = 'What crop is primarily grown in this field?'
        self.fields['livestock_type'].label = 'Livestock Type'
        self.fields['livestock_type'].help_text = 'If used for livestock, what type?'
    
    def clean_size(self):
        size = self.cleaned_data.get('size')
        if size and size <= 0:
            raise ValidationError('Field size must be greater than 0.')
        return size
    
    def clean(self):
        cleaned_data = super().clean()
        farm = cleaned_data.get('farm')
        name = cleaned_data.get('name')
        
        # Check if field name is unique within the farm
        if farm and name:
            existing_fields = FarmSection.objects.filter(farm=farm, name=name)
            if self.instance.pk:
                existing_fields = existing_fields.exclude(pk=self.instance.pk)
            
            if existing_fields.exists():
                raise ValidationError('A field with this name already exists in the selected farm.')
        
        return cleaned_data

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = [
            'name', 'scientific_name', 'description', 'growing_season', 
            'average_growing_period_days', 'ideal_temperature_min', 
            'ideal_temperature_max', 'ideal_rainfall_min', 'ideal_rainfall_max', 
            'ideal_soil_ph_min', 'ideal_soil_ph_max'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tomato, Corn, Wheat'}),
            'scientific_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Solanum lycopersicum'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of the crop'}),
            'growing_season': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Spring-Summer'}),
            'average_growing_period_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 90'}),
            'ideal_temperature_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°C'}),
            'ideal_temperature_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°C'}),
            'ideal_rainfall_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'ideal_rainfall_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'ideal_soil_ph_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g., 6.0'}),
            'ideal_soil_ph_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g., 7.0'}),
        }
        labels = {
            'average_growing_period_days': 'Avg. Growing Period (days)',
            'ideal_temperature_min': 'Min Ideal Temp (°C)',
            'ideal_temperature_max': 'Max Ideal Temp (°C)',
            'ideal_rainfall_min': 'Min Ideal Rainfall (mm)',
            'ideal_rainfall_max': 'Max Ideal Rainfall (mm)',
            'ideal_soil_ph_min': 'Min Ideal Soil pH',
            'ideal_soil_ph_max': 'Max Ideal Soil pH',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) # Assuming you might want to associate crops with users
        super().__init__(*args, **kwargs)
        # Add 'form-control' to all fields that don't have a specific widget defined
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs['class'] = 'form-check-input'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(instance, 'user'): # Check if model has user field
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class CropCycleForm(forms.ModelForm):
    """Form for creating and editing crop cycles"""
    
    class Meta:
        model = CropCycle
        fields = ['field', 'crop', 'crop_variety', 'planting_date', 'expected_harvest_date', 
                 'expected_yield_kg', 'status', 'notes']
        widgets = {
            'field': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_field'
            }),
            'crop': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_crop'
            }),
            'crop_variety': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_crop_variety'
            }),
            'planting_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_harvest_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_yield_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Expected yield in kg'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any notes about this crop cycle'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit field choices to user's fields
        if self.user:
            self.fields['field'].queryset = FarmSection.objects.filter(
                farm__owner=self.user, 
                is_active=True
            ).select_related('farm')
        
        # Get all crops
        self.fields['crop'].queryset = Crop.objects.all()
        
        # Initially empty crop variety choices (will be populated via AJAX)
        self.fields['crop_variety'].queryset = CropVariety.objects.none()
        self.fields['crop_variety'].required = False

        # Empty Labels
        self.fields['field'].empty_label = "Select a Field/Section"
        self.fields['crop'].empty_label = "Select a Crop Type"
        self.fields['crop_variety'].empty_label = "Select a Crop Variety"
        
        # Set default planting date to today
        if not self.instance.pk:
            self.fields['planting_date'].initial = date.today()
        
        # Update crop variety choices if crop is already selected
        if 'crop' in self.data:
            try:
                crop_id = int(self.data.get('crop'))
                self.fields['crop_variety'].queryset = CropVariety.objects.filter(crop_id=crop_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.crop:
            self.fields['crop_variety'].queryset = CropVariety.objects.filter(crop=self.instance.crop)
        
        # Add labels and help text
        self.fields['field'].label = 'Field/Section'
        self.fields['crop'].label = 'Crop Type'
        self.fields['crop_variety'].label = 'Crop Variety (Optional)'
        self.fields['planting_date'].label = 'Planting Date'
        self.fields['expected_harvest_date'].label = 'Expected Harvest Date'
        self.fields['expected_yield_kg'].label = 'Expected Yield (kg)'
        self.fields['expected_yield_kg'].help_text = 'Enter the expected yield in kilograms'
    
    def clean_planting_date(self):
        planting_date = self.cleaned_data.get('planting_date')
        if planting_date and planting_date > date.today() + timedelta(days=365):
            raise ValidationError('Planting date cannot be more than a year in the future.')
        return planting_date
    
    def clean_expected_harvest_date(self):
        expected_harvest_date = self.cleaned_data.get('expected_harvest_date')
        planting_date = self.cleaned_data.get('planting_date')
        
        if expected_harvest_date and planting_date:
            if expected_harvest_date <= planting_date:
                raise ValidationError('Expected harvest date must be after the planting date.')
        
        return expected_harvest_date
    
    def clean_expected_yield_kg(self):
        expected_yield = self.cleaned_data.get('expected_yield_kg')
        if expected_yield and expected_yield <= 0:
            raise ValidationError('Expected yield must be greater than 0.')
        return expected_yield
    
    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get('field')
        planting_date = cleaned_data.get('planting_date')
        crop = cleaned_data.get('crop')
        
        # Check for overlapping crop cycles in the same field
        if field and planting_date:
            overlapping_cycles = CropCycle.objects.filter(
                field=field,
                status__in=['planned', 'active']
            )
            
            if self.instance.pk:
                overlapping_cycles = overlapping_cycles.exclude(pk=self.instance.pk)
            
            for cycle in overlapping_cycles:
                if cycle.planting_date <= planting_date <= (cycle.expected_harvest_date or cycle.planting_date + timedelta(days=90)):
                    raise ValidationError(
                        f'This field already has an active crop cycle ({cycle.crop.name}) '
                        f'that overlaps with the selected planting date.'
                    )
        
        # Auto-calculate expected harvest date if not provided
        if crop and planting_date and not cleaned_data.get('expected_harvest_date'):
            if crop.average_growing_period_days:
                cleaned_data['expected_harvest_date'] = planting_date + timedelta(days=crop.average_growing_period_days)
        
        return cleaned_data

class FarmSectionFilterForm(forms.Form):
    """Form for filtering fields"""
    farm = forms.ModelChoiceField(
        queryset=Farm.objects.none(),
        required=False,
        empty_label="All Farms",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=user, is_active=True)

class CropCycleFilterForm(forms.Form):
    """Form for filtering crop cycles"""
    farm = forms.ModelChoiceField(
        queryset=Farm.objects.none(),
        required=False,
        empty_label="All Farms",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    crop = forms.ModelChoiceField(
        queryset=Crop.objects.all(),
        required=False,
        empty_label="All Crops",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + CropCycle.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=user, is_active=True)