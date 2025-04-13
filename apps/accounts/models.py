from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model for Gitako platform"""
    
    class UserType(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        FARMER = 'farmer', _('Farmer')
        SUPPLIER = 'supplier', _('Input Supplier')
        OFFTAKER = 'offtaker', _('Off-taker')
    
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.FARMER,
    )
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Location information
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Additional fields
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

class FarmerProfile(models.Model):
    """Extended profile for farmers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_size_hectares = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    years_of_experience = models.PositiveIntegerField(default=0)
    primary_crop = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Farmer Profile"

class SupplierProfile(models.Model):
    """Extended profile for input suppliers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    company_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, blank=True)
    product_categories = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.company_name} Supplier Profile"

class OfftakerProfile(models.Model):
    """Extended profile for off-takers/buyers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='offtaker_profile')
    company_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, blank=True)
    preferred_crops = models.JSONField(default=list)
    purchase_capacity = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.company_name} Off-taker Profile"