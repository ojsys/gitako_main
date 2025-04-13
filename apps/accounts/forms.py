from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 
                  'user_type', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create corresponding profile based on user type
            user_type = user.user_type
            if user_type == User.UserType.FARMER:
                from .models import FarmerProfile
                FarmerProfile.objects.create(user=user)
            elif user_type == User.UserType.SUPPLIER:
                from .models import SupplierProfile
                SupplierProfile.objects.create(user=user, company_name=f"{user.first_name}'s Company")
            elif user_type == User.UserType.OFFTAKER:
                from .models import OfftakerProfile
                OfftakerProfile.objects.create(user=user, company_name=f"{user.first_name}'s Company")
        
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                  'profile_picture', 'date_of_birth', 'address', 
                  'city', 'state', 'country']