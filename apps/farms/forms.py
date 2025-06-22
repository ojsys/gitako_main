# Create this as forms.py in your farms app

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Farm, FarmSection, Crop, CropVariety, CropCycle,
    CropCalendar, SeasonalPlanning, PlannedCropAllocation, CropRotationPlan
)
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
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter field name'})
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

class CropCalendarForm(forms.ModelForm):
    """Form for creating and editing crop calendar events"""
    
    class Meta:
        model = CropCalendar
        fields = [
            'farm', 'crop_cycle', 'event_type', 'title', 'description',
            'start_date', 'end_date', 'is_recurring', 'recurrence_pattern',
            'recurrence_interval', 'status', 'priority', 'assigned_to',
            'weather_dependent', 'min_temperature', 'max_temperature',
            'max_wind_speed', 'no_rain_required', 'estimated_cost'
        ]
        widgets = {
            'farm': forms.Select(attrs={'class': 'form-control'}),
            'crop_cycle': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence_pattern': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Pattern'),
                ('daily', 'Daily'),
                ('weekly', 'Weekly'),
                ('monthly', 'Monthly'),
            ]),
            'recurrence_interval': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'weather_dependent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'min_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'max_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'max_wind_speed': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1}),
            'no_rain_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit choices to user's farms and crop cycles
        if self.user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=self.user, is_active=True)
            self.fields['crop_cycle'].queryset = CropCycle.objects.filter(
                field__farm__owner=self.user
            ).select_related('crop', 'field')
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.fields['assigned_to'].queryset = User.objects.filter(
                farm_employments__farm__owner=self.user,
                farm_employments__is_active=True
            ).distinct()
        
        # Set empty labels
        self.fields['farm'].empty_label = "Select Farm"
        self.fields['crop_cycle'].empty_label = "Select Crop Cycle (Optional)"
        self.fields['assigned_to'].empty_label = "Assign to (Optional)"
        
        # Set initial values
        if not self.instance.pk:
            self.fields['start_date'].initial = date.today()
            self.fields['status'].initial = 'planned'
            self.fields['priority'].initial = 'medium'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_pattern = cleaned_data.get('recurrence_pattern')
        
        if end_date and start_date and end_date < start_date:
            raise ValidationError('End date must be after start date.')
        
        if is_recurring and not recurrence_pattern:
            raise ValidationError('Recurrence pattern is required for recurring events.')
        
        return cleaned_data

class SeasonalPlanningForm(forms.ModelForm):
    """Form for creating seasonal planning"""
    
    class Meta:
        model = SeasonalPlanning
        fields = [
            'farm', 'field', 'season_year', 'season', 'planning_notes',
            'soil_prep_required', 'irrigation_plan', 'fertilization_plan',
            'estimated_total_cost', 'estimated_revenue', 'status'
        ]
        widgets = {
            'farm': forms.Select(attrs={'class': 'form-control'}),
            'field': forms.Select(attrs={'class': 'form-control'}),
            'season_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2024}),
            'season': forms.Select(attrs={'class': 'form-control'}),
            'planning_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'soil_prep_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'irrigation_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fertilization_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'estimated_revenue': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=self.user, is_active=True)
            self.fields['field'].queryset = FarmSection.objects.filter(
                farm__owner=self.user, is_active=True
            ).select_related('farm')
        
        # Set initial values
        if not self.instance.pk:
            current_year = date.today().year
            self.fields['season_year'].initial = current_year
        
        # Set empty labels
        self.fields['farm'].empty_label = "Select Farm"
        self.fields['field'].empty_label = "Select Field"

class PlannedCropAllocationForm(forms.ModelForm):
    """Form for planned crop allocation within seasonal planning"""
    
    class Meta:
        model = PlannedCropAllocation
        fields = [
            'crop', 'crop_variety', 'allocated_area', 'expected_yield_per_hectare',
            'planned_planting_date', 'planned_harvest_date', 'estimated_cost_per_hectare',
            'expected_price_per_unit', 'notes'
        ]
        widgets = {
            'crop': forms.Select(attrs={'class': 'form-control'}),
            'crop_variety': forms.Select(attrs={'class': 'form-control'}),
            'allocated_area': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'expected_yield_per_hectare': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'planned_planting_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estimated_cost_per_hectare': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'expected_price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['crop'].queryset = Crop.objects.all()
        self.fields['crop_variety'].queryset = CropVariety.objects.none()
        
        # Set empty labels
        self.fields['crop'].empty_label = "Select Crop"
        self.fields['crop_variety'].empty_label = "Select Variety (Optional)"
        
        # Update crop variety choices if crop is selected
        if 'crop' in self.data:
            try:
                crop_id = int(self.data.get('crop'))
                self.fields['crop_variety'].queryset = CropVariety.objects.filter(crop_id=crop_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.crop:
            self.fields['crop_variety'].queryset = CropVariety.objects.filter(crop=self.instance.crop)
    
    def clean(self):
        cleaned_data = super().clean()
        planting_date = cleaned_data.get('planned_planting_date')
        harvest_date = cleaned_data.get('planned_harvest_date')
        allocated_area = cleaned_data.get('allocated_area')
        
        if harvest_date and planting_date and harvest_date <= planting_date:
            raise ValidationError('Harvest date must be after planting date.')
        
        if allocated_area and allocated_area <= 0:
            raise ValidationError('Allocated area must be greater than 0.')
        
        return cleaned_data

class CropRotationPlanForm(forms.ModelForm):
    """Form for creating crop rotation plans"""
    
    class Meta:
        model = CropRotationPlan
        fields = [
            'farm', 'field', 'plan_name', 'rotation_cycle_years',
            'year_1_crop', 'year_2_crop', 'year_3_crop', 'year_4_crop',
            'soil_health_benefits', 'pest_management_benefits',
            'economic_benefits', 'start_year', 'is_active'
        ]
        widgets = {
            'farm': forms.Select(attrs={'class': 'form-control'}),
            'field': forms.Select(attrs={'class': 'form-control'}),
            'plan_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter plan name'}),
            'rotation_cycle_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 4}),
            'year_1_crop': forms.Select(attrs={'class': 'form-control'}),
            'year_2_crop': forms.Select(attrs={'class': 'form-control'}),
            'year_3_crop': forms.Select(attrs={'class': 'form-control'}),
            'year_4_crop': forms.Select(attrs={'class': 'form-control'}),
            'soil_health_benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pest_management_benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'economic_benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2024}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['farm'].queryset = Farm.objects.filter(owner=self.user, is_active=True)
            self.fields['field'].queryset = FarmSection.objects.filter(
                farm__owner=self.user, is_active=True
            ).select_related('farm')
        
        # Set crop choices
        crop_queryset = Crop.objects.all()
        for field_name in ['year_1_crop', 'year_2_crop', 'year_3_crop', 'year_4_crop']:
            self.fields[field_name].queryset = crop_queryset
            if field_name != 'year_1_crop':
                self.fields[field_name].empty_label = "Select Crop (Optional)"
        
        # Set initial values
        if not self.instance.pk:
            current_year = date.today().year
            self.fields['start_year'].initial = current_year
            self.fields['rotation_cycle_years'].initial = 3
        
        # Set empty labels
        self.fields['farm'].empty_label = "Select Farm"
        self.fields['field'].empty_label = "Select Field"
        self.fields['year_1_crop'].empty_label = "Select Year 1 Crop"
    
    def clean(self):
        cleaned_data = super().clean()
        rotation_cycle_years = cleaned_data.get('rotation_cycle_years')
        
        # Ensure required crops are selected based on cycle years
        if rotation_cycle_years:
            required_crops = ['year_1_crop']
            if rotation_cycle_years >= 2:
                required_crops.append('year_2_crop')
            if rotation_cycle_years >= 3:
                required_crops.append('year_3_crop')
            if rotation_cycle_years >= 4:
                required_crops.append('year_4_crop')
            
            for crop_field in required_crops:
                if not cleaned_data.get(crop_field):
                    raise ValidationError(f'Crop for {crop_field.replace("_", " ").title()} is required for a {rotation_cycle_years}-year cycle.')
        
        return cleaned_data