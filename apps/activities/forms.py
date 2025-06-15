from django import forms
from .models import Activity


class ActivityForm(forms.ModelForm):
    """Form for creating and editing farm activities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add empty choice to select fields
        self.fields['field'].empty_label = "Select Field"
        self.fields['crop_cycle'].empty_label = "Select Crop Cycle"
        self.fields['activity_type'].empty_label = "Select Activity Type"
        self.fields['status'].empty_label = "Select Status"
        
        # Make select fields required (remove blank option)
        self.fields['field'].required = True
        self.fields['activity_type'].required = True
        self.fields['status'].required = True
        
        # Optional: Add CSS classes for styling
        self.fields['field'].widget.attrs.update({'class': 'form-control'})
        self.fields['crop_cycle'].widget.attrs.update({'class': 'form-control'})
        self.fields['activity_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
    
    class Meta:
        model = Activity
        fields = [
            'field', 'crop_cycle', 'activity_type', 'planned_date', 
            'actual_date', 'status', 'title', 'description', 'notes',
            'labor_cost', 'material_cost', 'other_cost',
            'temperature', 'humidity', 'weather_notes'
        ]
        widgets = {
            'planned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'weather_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'labor_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'material_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'humidity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean_field(self):
        field = self.cleaned_data.get('field')
        if not field:
            raise forms.ValidationError("Please select a field.")
        return field
    
    def clean_activity_type(self):
        activity_type = self.cleaned_data.get('activity_type')
        if not activity_type:
            raise forms.ValidationError("Please select an activity type.")
        return activity_type
    
    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not status:
            raise forms.ValidationError("Please select a status.")
        return status
    
    def clean_planned_date(self):
        planned_date = self.cleaned_data.get('planned_date')
        if not planned_date:
            raise forms.ValidationError("Please select a date.")
        return planned_date

    def clean_actual_date(self):
        actual_date = self.cleaned_data.get('actual_date')
        if not actual_date:
            raise forms.ValidationError("Please select a date.")
        return actual_date
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("Please enter a title.")
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError("Please enter a description.")
        return description
    
    def clean_notes(self):
        notes = self.cleaned_data.get('notes')
        if not notes:
            raise forms.ValidationError("Please enter notes.")
        return notes
    
    def clean_labor_cost(self):
        labor_cost = self.cleaned_data.get('labor_cost')
        if labor_cost is None:
            raise forms.ValidationError("Please enter a labor cost.")
        return labor_cost
    
    def clean_material_cost(self):
        material_cost = self.cleaned_data.get('material_cost')
        if material_cost is None:
            raise forms.ValidationError("Please enter a material cost.")
        return material_cost
    
    def clean_other_cost(self):
        other_cost = self.cleaned_data.get('other_cost')
        if other_cost is None:
            raise forms.ValidationError("Please enter an other cost.")
        return other_cost



# class ActivityForm(forms.ModelForm):
#     """Form for creating and editing farm activities"""
    
#     class Meta:
#         model = Activity
#         fields = [
#             'field', 'crop_cycle', 'activity_type', 'planned_date', 
#             'actual_date', 'status', 'title', 'description', 'notes',
#             'labor_cost', 'material_cost', 'other_cost',
#             'temperature', 'humidity', 'weather_notes'
#         ]
#         widgets = {
#             'planned_date': forms.DateInput(attrs={'type': 'date'}),
#             'actual_date': forms.DateInput(attrs={'type': 'date'}),
#             'description': forms.Textarea(attrs={'rows': 3}),
#             'notes': forms.Textarea(attrs={'rows': 2}),
#             'weather_notes': forms.TextInput(),
#         }