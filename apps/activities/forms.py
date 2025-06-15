from django import forms
from .models import Activity

class ActivityForm(forms.ModelForm):
    """Form for creating and editing farm activities"""
    
    class Meta:
        model = Activity
        fields = [
            'field', 'crop_cycle', 'activity_type', 'planned_date', 
            'actual_date', 'status', 'title', 'description', 'notes',
            'labor_cost', 'material_cost', 'other_cost',
            'temperature', 'humidity', 'weather_notes'
        ]
        widgets = {
            'planned_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'weather_notes': forms.TextInput(),
        }