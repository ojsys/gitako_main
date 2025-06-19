from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import Activity
from .forms import ActivityForm
from apps.farms.models import CropCycle, FarmSection

@login_required
def activity_list(request):
    """View to display all activities"""
    activities = Activity.objects.filter(
        field__farm__owner=request.user
    ).select_related('field', 'crop_cycle').order_by('-planned_date')
    
    context = {
        'activities': activities,
        'active_page': 'activities'
    }
    return render(request, 'activities/activity_list.html', context)

@login_required
def activity_create(request, crop_cycle_id=None):
    """View to create a new activity"""
    initial_data = {}
    
    # If crop_cycle_id is provided, pre-fill the form
    if crop_cycle_id:
        crop_cycle = get_object_or_404(CropCycle, id=crop_cycle_id, field__farm__owner=request.user)
        initial_data = {
            'crop_cycle': crop_cycle,
            'field': crop_cycle.field
        }
    
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)  # Don't save to DB yet
            activity.created_by = request.user  # Set the created_by field
            activity.save()  # Now save to DB
            messages.success(request, 'Activity created successfully!')
            
            # Redirect based on where the request came from
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('activities:activity_detail', activity_id=activity.id)
    else:
        form = ActivityForm(initial=initial_data)
        
        # Filter field choices to only show fields owned by the user
        form.fields['field'].queryset = FarmSection.objects.filter(farm__owner=request.user)
        
        # Filter crop_cycle choices based on the selected field
        if crop_cycle_id:
            form.fields['crop_cycle'].queryset = CropCycle.objects.filter(
                field__farm__owner=request.user,
                field=crop_cycle.field
            )
        else:
            form.fields['crop_cycle'].queryset = CropCycle.objects.filter(
                field__farm__owner=request.user
            )
    
    context = {
        'form': form,
        'active_page': 'activities',
        'is_create': True
    }
    return render(request, 'activities/activity_form.html', context)

@login_required
def activity_edit(request, activity_id):
    """View to edit an existing activity"""
    activity = get_object_or_404(Activity, id=activity_id, field__farm__owner=request.user)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully!')
            
            # Redirect based on where the request came from
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('activities:activity_detail', activity_id=activity.id)
    else:
        form = ActivityForm(instance=activity)
        
        # Filter field choices to only show fields owned by the user
        form.fields['field'].queryset = FarmSection.objects.filter(farm__owner=request.user)
        
        # Filter crop_cycle choices based on the selected field
        form.fields['crop_cycle'].queryset = CropCycle.objects.filter(
            field__farm__owner=request.user,
            field=activity.field
        )
    
    context = {
        'form': form,
        'activity': activity,
        'active_page': 'activities',
        'is_edit': True
    }
    return render(request, 'activities/activity_form.html', context)

@login_required
def activity_detail(request, activity_id):
    """View to display activity details"""
    activity = get_object_or_404(Activity, id=activity_id, field__farm__owner=request.user)
    
    context = {
        'activity': activity,
        'active_page': 'activities'
    }
    return render(request, 'activities/activity_detail.html', context)

@login_required
def activity_delete(request, activity_id):
    """View to delete an activity"""
    activity = get_object_or_404(Activity, id=activity_id, field__farm__owner=request.user)
    
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Activity deleted successfully!')
        
        # Redirect based on where the request came from
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        return redirect('activities:activity_list')
    
    context = {
        'activity': activity,
        'active_page': 'activities'
    }
    return render(request, 'activities/activity_confirm_delete.html', context)

@login_required
def mark_activity_complete(request, activity_id):
    """View to mark an activity as completed"""
    activity = get_object_or_404(Activity, id=activity_id, field__farm__owner=request.user)
    
    if request.method == 'POST':
        activity.status = 'completed'
        activity.actual_date = timezone.now().date()
        activity.save()
        messages.success(request, 'Activity marked as completed!')
    
    # Redirect back to the referring page
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    return redirect('activities:activity_detail', activity_id=activity.id)



@login_required
def mark_activity_incomplete(request, activity_id):
    """View to mark an activity as incomplete"""
    activity = get_object_or_404(Activity, id=activity_id, field__farm__owner=request.user)
    
    if request.method == 'POST':
        activity.status = 'incomplete'
        activity.actual_date = None
        activity.save()
        messages.success(request, 'Activity marked as incomplete!')
    
    # Redirect back to the referring page
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    return redirect('activities:activity_detail', activity_id=activity.id)

