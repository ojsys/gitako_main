from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

from .models import (
    Activity, ActivityImage, PlantingActivity, FertilizerActivity, 
    PestControlActivity, IrrigationActivity, HarvestActivity, ActivityReminder
)
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

# Enhanced Farm Records Views
@login_required
def farm_records_dashboard(request):
    """Comprehensive farm records dashboard"""
    from django.db.models import Count, Sum, Avg, Q
    from datetime import datetime, timedelta
    
    today = timezone.now().date()
    this_week = today - timedelta(days=7)
    this_month = today - timedelta(days=30)
    
    # Activity statistics
    activities = Activity.objects.filter(field__farm__owner=request.user)
    
    # Recent activities
    recent_activities = activities.filter(
        actual_date__gte=this_week
    ).select_related('field', 'crop_cycle').order_by('-actual_date')[:10]
    
    # Upcoming activities
    upcoming_activities = activities.filter(
        planned_date__gte=today,
        status__in=['planned', 'in_progress']
    ).select_related('field', 'crop_cycle').order_by('planned_date')[:10]
    
    # Overdue activities
    overdue_activities = activities.filter(
        planned_date__lt=today,
        status__in=['planned', 'in_progress']
    ).select_related('field', 'crop_cycle').order_by('planned_date')
    
    # Activity type breakdown
    activity_breakdown = activities.filter(
        actual_date__gte=this_month
    ).values('activity_type').annotate(
        count=Count('id'),
        total_cost=Sum('labor_cost') + Sum('material_cost') + Sum('other_cost')
    ).order_by('-count')
    
    # Cost analysis
    total_costs = activities.filter(
        actual_date__gte=this_month
    ).aggregate(
        total_labor=Sum('labor_cost') or 0,
        total_material=Sum('material_cost') or 0,
        total_other=Sum('other_cost') or 0
    )
    
    # Field activity summary
    field_activity = activities.filter(
        actual_date__gte=this_month
    ).values(
        'field__name', 'field__farm__name'
    ).annotate(
        activity_count=Count('id'),
        total_cost=Sum('labor_cost') + Sum('material_cost') + Sum('other_cost')
    ).order_by('-activity_count')[:5]
    
    # Weather tracking for recent activities
    weather_data = activities.filter(
        actual_date__gte=this_week,
        temperature__isnull=False
    ).values('actual_date').annotate(
        avg_temp=Avg('temperature'),
        avg_humidity=Avg('humidity')
    ).order_by('actual_date')
    
    context = {
        'recent_activities': recent_activities,
        'upcoming_activities': upcoming_activities,
        'overdue_activities': overdue_activities,
        'activity_breakdown': activity_breakdown,
        'total_costs': total_costs,
        'field_activity': field_activity,
        'weather_data': json.dumps(list(weather_data), default=str),
        'stats': {
            'total_activities': activities.count(),
            'completed_this_month': activities.filter(
                actual_date__gte=this_month, status='completed'
            ).count(),
            'pending_activities': activities.filter(
                status__in=['planned', 'in_progress']
            ).count(),
            'overdue_count': overdue_activities.count(),
        },
        'active_page': 'records'
    }
    
    return render(request, 'activities/farm_records_dashboard.html', context)

@login_required
def activity_analytics(request):
    """Activity analytics and reporting"""
    from django.db.models import Count, Sum, Avg, F
    from datetime import datetime, timedelta
    
    # Get date range from request
    days = int(request.GET.get('days', 90))
    start_date = timezone.now().date() - timedelta(days=days)
    
    activities = Activity.objects.filter(
        field__farm__owner=request.user,
        actual_date__gte=start_date
    )
    
    # Activity trends over time
    activity_trends = activities.values('actual_date').annotate(
        count=Count('id'),
        total_cost=Sum(F('labor_cost') + F('material_cost') + F('other_cost'))
    ).order_by('actual_date')
    
    # Cost breakdown by activity type
    cost_breakdown = activities.values('activity_type').annotate(
        total_cost=Sum(F('labor_cost') + F('material_cost') + F('other_cost')),
        avg_cost=Avg(F('labor_cost') + F('material_cost') + F('other_cost')),
        count=Count('id')
    ).order_by('-total_cost')
    
    # Efficiency metrics
    efficiency_data = activities.filter(
        status='completed'
    ).annotate(
        days_difference=F('actual_date') - F('planned_date')
    ).values('activity_type').annotate(
        avg_delay=Avg('days_difference'),
        on_time_count=Count('id', filter=Q(actual_date__lte=F('planned_date'))),
        total_count=Count('id')
    )
    
    # Seasonal patterns
    seasonal_data = activities.extra(
        select={'month': "EXTRACT(month FROM actual_date)"}
    ).values('month', 'activity_type').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Labor productivity
    labor_productivity = activities.exclude(
        labor_cost=0
    ).values('activity_type').annotate(
        total_labor_cost=Sum('labor_cost'),
        total_activities=Count('id'),
        avg_labor_per_activity=Avg('labor_cost')
    ).order_by('-total_labor_cost')
    
    context = {
        'activity_trends': json.dumps(list(activity_trends), default=str),
        'cost_breakdown': cost_breakdown,
        'efficiency_data': efficiency_data,
        'seasonal_data': json.dumps(list(seasonal_data), default=str),
        'labor_productivity': labor_productivity,
        'date_range': days,
        'total_activities': activities.count(),
        'total_cost': activities.aggregate(
            total=Sum(F('labor_cost') + F('material_cost') + F('other_cost'))
        )['total'] or 0,
        'active_page': 'records'
    }
    
    return render(request, 'activities/activity_analytics.html', context)

@login_required
def activity_calendar(request):
    """Calendar view of all farm activities"""
    import calendar
    from datetime import datetime
    
    # Get current month/year or from request
    current_date = timezone.now().date()
    year = int(request.GET.get('year', current_date.year))
    month = int(request.GET.get('month', current_date.month))
    
    # Calculate previous and next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
        
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    # Get activities for the month
    activities = Activity.objects.filter(
        field__farm__owner=request.user,
        planned_date__year=year,
        planned_date__month=month
    ).select_related('field', 'crop_cycle')
    
    # Group activities by date
    activities_by_date = {}
    for activity in activities:
        date_key = activity.planned_date
        if date_key not in activities_by_date:
            activities_by_date[date_key] = []
        activities_by_date[date_key].append(activity)
    
    # Generate calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    context = {
        'activities': activities,
        'activities_by_date': activities_by_date,
        'calendar_data': cal,
        'current_month': month,
        'current_year': year,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': current_date,
        'active_page': 'records'
    }
    
    return render(request, 'activities/activity_calendar.html', context)

@login_required
def planting_records(request):
    """Specialized view for planting records"""
    planting_activities = Activity.objects.filter(
        field__farm__owner=request.user,
        activity_type='planting'
    ).select_related('field', 'crop_cycle').order_by('-actual_date')
    
    # Get planting details
    planting_details = []
    for activity in planting_activities:
        try:
            detail = PlantingActivity.objects.get(activity=activity)
            planting_details.append({
                'activity': activity,
                'detail': detail
            })
        except PlantingActivity.DoesNotExist:
            planting_details.append({
                'activity': activity,
                'detail': None
            })
    
    # Planting statistics
    total_plantings = planting_activities.count()
    total_seed_cost = planting_activities.aggregate(
        total=Sum('material_cost')
    )['total'] or 0
    
    context = {
        'planting_details': planting_details,
        'total_plantings': total_plantings,
        'total_seed_cost': total_seed_cost,
        'active_page': 'records'
    }
    
    return render(request, 'activities/planting_records.html', context)

@login_required
def harvest_records(request):
    """Specialized view for harvest records"""
    harvest_activities = Activity.objects.filter(
        field__farm__owner=request.user,
        activity_type='harvesting'
    ).select_related('field', 'crop_cycle').order_by('-actual_date')
    
    # Get harvest details
    harvest_details = []
    total_yield = 0
    
    for activity in harvest_activities:
        try:
            detail = HarvestActivity.objects.get(activity=activity)
            harvest_details.append({
                'activity': activity,
                'detail': detail
            })
            # Convert yield to kg for totaling
            yield_kg = detail.yield_quantity
            if detail.yield_unit.lower() in ['ton', 'tons']:
                yield_kg *= 1000
            total_yield += yield_kg
        except HarvestActivity.DoesNotExist:
            harvest_details.append({
                'activity': activity,
                'detail': None
            })
    
    # Harvest statistics by crop
    harvest_by_crop = {}
    for item in harvest_details:
        if item['detail'] and item['activity'].crop_cycle:
            crop_name = item['activity'].crop_cycle.crop.name
            if crop_name not in harvest_by_crop:
                harvest_by_crop[crop_name] = {
                    'total_yield': 0,
                    'harvest_count': 0,
                    'total_value': 0
                }
            
            yield_kg = item['detail'].yield_quantity
            if item['detail'].yield_unit.lower() in ['ton', 'tons']:
                yield_kg *= 1000
                
            harvest_by_crop[crop_name]['total_yield'] += yield_kg
            harvest_by_crop[crop_name]['harvest_count'] += 1
    
    context = {
        'harvest_details': harvest_details,
        'total_harvests': harvest_activities.count(),
        'total_yield': total_yield,
        'harvest_by_crop': harvest_by_crop,
        'active_page': 'records'
    }
    
    return render(request, 'activities/harvest_records.html', context)

@login_required
def weather_records(request):
    """Weather data tracking from activities"""
    activities_with_weather = Activity.objects.filter(
        field__farm__owner=request.user,
        temperature__isnull=False
    ).order_by('-actual_date')[:50]
    
    # Weather trends
    weather_trends = activities_with_weather.values('actual_date').annotate(
        avg_temp=Avg('temperature'),
        avg_humidity=Avg('humidity')
    ).order_by('actual_date')
    
    # Weather by activity type
    weather_by_activity = activities_with_weather.values('activity_type').annotate(
        avg_temp=Avg('temperature'),
        avg_humidity=Avg('humidity'),
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'activities_with_weather': activities_with_weather,
        'weather_trends': json.dumps(list(weather_trends), default=str),
        'weather_by_activity': weather_by_activity,
        'active_page': 'records'
    }
    
    return render(request, 'activities/weather_records.html', context)

# AJAX Views
@login_required
def add_activity_image(request, activity_id):
    """AJAX view to add images to activities"""
    if request.method == 'POST':
        activity = get_object_or_404(Activity, id=activity_id, field__farm__owner=request.user)
        
        if 'image' in request.FILES:
            image = ActivityImage.objects.create(
                activity=activity,
                image=request.FILES['image'],
                caption=request.POST.get('caption', '')
            )
            
            return JsonResponse({
                'success': True,
                'image_id': image.id,
                'image_url': image.image.url,
                'caption': image.caption
            })
    
    return JsonResponse({'success': False})

@login_required
def activity_quick_complete(request, activity_id):
    """AJAX view to quickly mark activity as complete"""
    if request.method == 'POST':
        activity = get_object_or_404(Activity, id=activity_id, field__farm__owner=request.user)
        
        activity.status = 'completed'
        activity.actual_date = timezone.now().date()
        
        # Update costs if provided
        if 'labor_cost' in request.POST:
            activity.labor_cost = request.POST.get('labor_cost', 0)
        if 'material_cost' in request.POST:
            activity.material_cost = request.POST.get('material_cost', 0)
        if 'notes' in request.POST:
            activity.notes = request.POST.get('notes', '')
            
        activity.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Activity "{activity.title}" marked as completed.'
        })
    
    return JsonResponse({'success': False})

@login_required
def get_field_crop_cycles(request):
    """AJAX view to get crop cycles for a selected field"""
    field_id = request.GET.get('field_id')
    if field_id:
        crop_cycles = CropCycle.objects.filter(
            field_id=field_id,
            field__farm__owner=request.user
        ).values('id', 'crop__name', 'planting_date', 'status')
        
        return JsonResponse({
            'success': True,
            'crop_cycles': list(crop_cycles)
        })
    
    return JsonResponse({'success': False})

