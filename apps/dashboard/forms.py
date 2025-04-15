from django import forms
from apps.accounts.models import User, FarmerProfile, SupplierProfile, OfftakerProfile

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                  'date_of_birth', 'profile_picture', 'address', 
                  'city', 'state', 'country']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class FarmerProfileForm(forms.ModelForm):
    """Form for updating farmer-specific profile information"""
    
    class Meta:
        model = FarmerProfile
        fields = ['farm_size_hectares', 'years_of_experience', 'primary_crop']

class SupplierProfileForm(forms.ModelForm):
    """Form for updating supplier-specific profile information"""
    product_categories = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter product categories separated by commas",
        required=False
    )
    
    class Meta:
        model = SupplierProfile
        fields = ['company_name', 'business_registration_number', 'product_categories']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert list to comma-separated string for display
        if self.instance and self.instance.product_categories:
            self.initial['product_categories'] = ', '.join(self.instance.product_categories)
    
    def clean_product_categories(self):
        # Convert comma-separated string to list
        categories = self.cleaned_data.get('product_categories', '')
        if categories:
            return [cat.strip() for cat in categories.split(',') if cat.strip()]
        return []

class OfftakerProfileForm(forms.ModelForm):
    """Form for updating offtaker-specific profile information"""
    preferred_crops = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter preferred crops separated by commas",
        required=False
    )
    
    class Meta:
        model = OfftakerProfile
        fields = ['company_name', 'business_registration_number', 'preferred_crops', 'purchase_capacity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert list to comma-separated string for display
        if self.instance and self.instance.preferred_crops:
            self.initial['preferred_crops'] = ', '.join(self.instance.preferred_crops)
    
    def clean_preferred_crops(self):
        # Convert comma-separated string to list
        crops = self.cleaned_data.get('preferred_crops', '')
        if crops:
            return [crop.strip() for crop in crops.split(',') if crop.strip()]
        return []