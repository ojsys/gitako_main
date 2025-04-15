from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FarmerProfile, SupplierProfile, OfftakerProfile

class FarmerProfileInline(admin.StackedInline):
    model = FarmerProfile
    can_delete = False
    verbose_name_plural = 'Farmer Profile'
    fk_name = 'user'

class SupplierProfileInline(admin.StackedInline):
    model = SupplierProfile
    can_delete = False
    verbose_name_plural = 'Supplier Profile'
    fk_name = 'user'

class OfftakerProfileInline(admin.StackedInline):
    model = OfftakerProfile
    can_delete = False
    verbose_name_plural = 'Offtaker Profile'
    fk_name = 'user'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 
                    'is_verified', 'is_active', 'profile_picture_thumbnail', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 
                                     'date_of_birth', 'profile_picture')}),
        ('Location', {'fields': ('address', 'city', 'state', 'country', 'latitude', 'longitude')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('User Type', {'fields': ('user_type',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == User.UserType.FARMER:
                return [FarmerProfileInline]
            elif obj.user_type == User.UserType.SUPPLIER:
                return [SupplierProfileInline]
            elif obj.user_type == User.UserType.OFFTAKER:
                return [OfftakerProfileInline]
        return []
    
    def profile_picture_thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', 
                              obj.profile_picture.url)
        return format_html('<span style="color: #999;">No Image</span>')
    profile_picture_thumbnail.short_description = 'Profile Picture'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Create corresponding profile if it doesn't exist
        if not change:  # Only for new users
            if obj.user_type == User.UserType.FARMER and not hasattr(obj, 'farmer_profile'):
                FarmerProfile.objects.create(user=obj)
            elif obj.user_type == User.UserType.SUPPLIER and not hasattr(obj, 'supplier_profile'):
                SupplierProfile.objects.create(user=obj)
            elif obj.user_type == User.UserType.OFFTAKER and not hasattr(obj, 'offtaker_profile'):
                OfftakerProfile.objects.create(user=obj)

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_size_hectares', 'years_of_experience', 'primary_crop')
    search_fields = ('user__username', 'user__email', 'primary_crop')
    list_filter = ('years_of_experience',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user',)
        return ()

@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'business_registration_number', 'display_product_categories')
    search_fields = ('user__username', 'user__email', 'company_name', 'business_registration_number')
    
    def display_product_categories(self, obj):
        if obj.product_categories:
            return ", ".join(obj.product_categories)
        return "-"
    display_product_categories.short_description = 'Product Categories'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user',)
        return ()

@admin.register(OfftakerProfile)
class OfftakerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'business_registration_number', 'display_preferred_crops', 'purchase_capacity')
    search_fields = ('user__username', 'user__email', 'company_name', 'business_registration_number')
    
    def display_preferred_crops(self, obj):
        if obj.preferred_crops:
            return ", ".join(obj.preferred_crops)
        return "-"
    display_preferred_crops.short_description = 'Preferred Crops'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user',)
        return ()
