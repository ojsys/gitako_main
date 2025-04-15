from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.models import FarmerProfile, SupplierProfile, OfftakerProfile
from .forms import UserProfileForm, FarmerProfileForm, SupplierProfileForm, OfftakerProfileForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
import csv
from io import StringIO
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import DashboardWidget, UserDashboardLayout
from apps.accounts.models import User, FarmerProfile, SupplierProfile, OfftakerProfile

@login_required
def dashboard(request):
    """Main dashboard view"""
    user = request.user
    
    # Get user-specific widgets and global widgets
    user_widgets = DashboardWidget.objects.filter(user=user, is_active=True)
    global_widgets = DashboardWidget.objects.filter(is_global=True, is_active=True)
    
    # Combine and sort by order
    widgets = list(user_widgets) + list(global_widgets)
    widgets.sort(key=lambda x: x.order)
    
    # Get user profile based on user type
    profile = None
    if user.user_type == User.UserType.FARMER:
        profile = getattr(user, 'farmer_profile', None)
    elif user.user_type == User.UserType.SUPPLIER:
        profile = getattr(user, 'supplier_profile', None)
    elif user.user_type == User.UserType.OFFTAKER:
        profile = getattr(user, 'offtaker_profile', None)
    
    # Get dashboard metrics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Users created in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Count by user type
    total_farmers = User.objects.filter(user_type=User.UserType.FARMER).count()
    total_suppliers = User.objects.filter(user_type=User.UserType.SUPPLIER).count()
    total_offtakers = User.objects.filter(user_type=User.UserType.OFFTAKER).count()
    
    context = {
        'widgets': widgets,
        'user_type': user.user_type,
        'profile': profile,
        'active_page': 'dashboard',
        'total_users': total_users,
        'active_users': active_users,
        'new_users': new_users,
        'total_farmers': total_farmers,
        'total_suppliers': total_suppliers,
        'total_offtakers': total_offtakers,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def profile_view(request):
    """View and edit user profile"""
    user = request.user
    
    # Get or create the specific profile based on user type
    profile = None
    if user.user_type == 'farmer':
        profile, created = FarmerProfile.objects.get_or_create(user=user)
    elif user.user_type == 'supplier':
        profile, created = SupplierProfile.objects.get_or_create(user=user)
    elif user.user_type == 'offtaker':
        profile, created = OfftakerProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Handle user form
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        # Handle specific profile form based on user type
        if user.user_type == 'farmer':
            profile_form = FarmerProfileForm(request.POST, instance=profile)
        elif user.user_type == 'supplier':
            profile_form = SupplierProfileForm(request.POST, instance=profile)
        elif user.user_type == 'offtaker':
            profile_form = OfftakerProfileForm(request.POST, instance=profile)
        else:
            profile_form = None
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:profile')
    else:
        # Create forms with current data
        user_form = UserProfileForm(instance=user)
        
        # Add CSS classes to form fields
        for field_name, field in user_form.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        if user.user_type == 'farmer':
            profile_form = FarmerProfileForm(instance=profile)
        elif user.user_type == 'supplier':
            profile_form = SupplierProfileForm(instance=profile)
        elif user.user_type == 'offtaker':
            profile_form = OfftakerProfileForm(instance=profile)
        else:
            profile_form = None
        
        # Add CSS classes to profile form fields if it exists
        if profile_form:
            for field_name, field in profile_form.fields.items():
                field.widget.attrs.update({'class': 'form-control'})
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'active_page': 'profile',
    }
    
    return render(request, 'dashboard/profile.html', context)

@login_required
def settings(request):
    """User settings view"""
    user = request.user
    
    context = {
        'user': user,
        'active_page': 'settings',
    }
    
    return render(request, 'dashboard/settings.html', context)

@login_required
@require_POST
def update_settings(request):
    """Update user settings"""
    user = request.user
    
    # Get or create user settings
    if not hasattr(user, 'settings'):
        user.settings = {}
    
    # Update notification settings
    user.settings['email_notifications'] = 'email_notifications' in request.POST
    user.settings['sms_notifications'] = 'sms_notifications' in request.POST
    user.settings['push_notifications'] = 'push_notifications' in request.POST
    
    # Update dashboard preferences
    user.settings['default_dashboard'] = request.POST.get('default_dashboard', 'standard')
    user.settings['show_weather'] = 'show_weather' in request.POST
    user.settings['show_tasks'] = 'show_tasks' in request.POST
    user.settings['show_analytics'] = 'show_analytics' in request.POST
    
    # Update language and region settings
    user.settings['language'] = request.POST.get('language', 'en')
    user.settings['timezone'] = request.POST.get('timezone', 'UTC')
    
    # Update privacy settings
    user.settings['public_profile'] = 'public_profile' in request.POST
    user.settings['share_location'] = 'share_location' in request.POST
    user.settings['data_analytics'] = 'data_analytics' in request.POST
    
    # Save user
    user.save()
    
    messages.success(request, 'Settings updated successfully!')
    return redirect('dashboard:settings')

@login_required
def export_data(request):
    """Export user data"""
    user = request.user
    
    # Create CSV file
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    
    # Write user information
    writer.writerow(['User Information'])
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Phone Number', 'Date of Birth'])
    writer.writerow([user.username, user.email, user.first_name, user.last_name, user.phone_number, user.date_of_birth])
    
    writer.writerow([])  # Empty row for separation
    
    # Write address information
    writer.writerow(['Address Information'])
    writer.writerow(['Address', 'City', 'State/Province', 'Country'])
    writer.writerow([user.address, user.city, user.state, user.country])
    
    writer.writerow([])  # Empty row for separation
    
    # Write profile information based on user type
    if user.user_type == User.UserType.FARMER:
        profile = getattr(user, 'farmer_profile', None)
        if profile:
            writer.writerow(['Farmer Information'])
            writer.writerow(['Farm Size (hectares)', 'Years of Experience', 'Primary Crop'])
            writer.writerow([profile.farm_size_hectares, profile.years_of_experience, profile.primary_crop])
    elif user.user_type == User.UserType.SUPPLIER:
        profile = getattr(user, 'supplier_profile', None)
        if profile:
            writer.writerow(['Supplier Information'])
            writer.writerow(['Company Name', 'Business Registration Number'])
            writer.writerow([profile.company_name, profile.business_registration_number])
    elif user.user_type == User.UserType.OFFTAKER:
        profile = getattr(user, 'offtaker_profile', None)
        if profile:
            writer.writerow(['Off-taker Information'])
            writer.writerow(['Company Name', 'Business Registration Number', 'Purchase Capacity'])
            writer.writerow([profile.company_name, profile.business_registration_number, profile.purchase_capacity])
    
    # Create response
    response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_data.csv"'
    
    return response

@login_required
@require_POST
def delete_account(request):
    """Delete user account"""
    user = request.user
    password = request.POST.get('password', '')
    
    # Check if password is correct
    if not user.check_password(password):
        messages.error(request, 'Incorrect password. Account deletion failed.')
        return redirect('dashboard:settings')
    
    # Log the user out and delete the account
    user.delete()
    messages.success(request, 'Your account has been deleted.')
    return redirect('accounts:login')

@login_required
@require_POST
def save_layout(request):
    """Save user dashboard layout preferences"""
    try:
        data = json.loads(request.body)
        layout = data.get('layout', {})
        
        # Get or create user dashboard layout
        user_layout, created = UserDashboardLayout.objects.get_or_create(user=request.user)
        user_layout.layout = layout
        user_layout.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
