from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, F
from django.http import JsonResponse
from .models import Farm, FarmSection, Crop, CropVariety, CropCycle
from django.utils import timezone
from datetime import timedelta

# Add these imports at the top
from apps.activities.models import Activity
from apps.financials.models import Budget, BudgetItem


@login_required
def crop_list(request):
    """View to display all crops"""
    # Get all crops
    crops = Crop.objects.all()
    
    # Get user's farms
    farms = Farm.objects.filter(owner=request.user)
    
    # Get active crop cycles for the user's farms
    active_crop_cycles = CropCycle.objects.filter(
        field__farm__owner=request.user,
        status__in=['planned', 'active']
    ).select_related('crop', 'field')
    
    # Count crops by type
    crop_distribution = CropCycle.objects.filter(
        field__farm__owner=request.user,
        status__in=['planned', 'active']
    ).values('crop__name').annotate(
        count=Count('id'),
        total_area=Sum('field__size')
    ).order_by('-total_area')
    
    # Calculate expected yields
    total_expected_yield = CropCycle.objects.filter(
        field__farm__owner=request.user,
        status__in=['planned', 'active']
    ).aggregate(total=Sum('expected_yield_kg'))['total'] or 0
    
    context = {
        'crops': crops,
        'active_crop_cycles': active_crop_cycles,
        'crop_distribution': crop_distribution,
        'total_expected_yield': total_expected_yield,
        'farms': farms,
        'active_page': 'crops'
    }
    
    return render(request, 'farms/crop_list.html', context)

@login_required
def crop_detail(request, crop_id):
    """View to display details of a specific crop"""
    crop = get_object_or_404(Crop, id=crop_id)
    varieties = CropVariety.objects.filter(crop=crop)
    
    # Get user's crop cycles for this crop
    crop_cycles = CropCycle.objects.filter(
        field__farm__owner=request.user,
        crop=crop
    ).select_related('field', 'field__farm')
    
    # Active crop cycles
    active_cycles = crop_cycles.filter(status__in=['planned', 'active'])
    
    # Historical crop cycles
    historical_cycles = crop_cycles.filter(status__in=['harvested', 'failed'])
    
    context = {
        'crop': crop,
        'varieties': varieties,
        'active_cycles': active_cycles,
        'historical_cycles': historical_cycles,
        'active_page': 'crops'
    }
    
    return render(request, 'farms/crop_detail.html', context)

@login_required
def crop_cycle_list(request):
    """View to display all crop cycles"""
    # Get user's farms
    farms = Farm.objects.filter(owner=request.user)
    
    # Get all crop cycles for the user's farms
    crop_cycles = CropCycle.objects.filter(
        field__farm__owner=request.user
    ).select_related('crop', 'field', 'field__farm')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        crop_cycles = crop_cycles.filter(status=status_filter)
    
    # Filter by farm if provided
    farm_filter = request.GET.get('farm')
    if farm_filter:
        crop_cycles = crop_cycles.filter(field__farm__id=farm_filter)
    
    # Filter by crop if provided
    crop_filter = request.GET.get('crop')
    if crop_filter:
        crop_cycles = crop_cycles.filter(crop__id=crop_filter)
    
    # Get all crops for filtering
    crops = Crop.objects.all()
    
    context = {
        'crop_cycles': crop_cycles,
        'farms': farms,
        'crops': crops,
        'active_page': 'crops',
        'status_filter': status_filter,
        'farm_filter': farm_filter,
        'crop_filter': crop_filter
    }
    
    return render(request, 'farms/crop_cycle_list.html', context)

@login_required
def crop_dashboard(request, crop_cycle_id=None):
    """Dashboard view for crops"""
    if crop_cycle_id:
        crop_cycle = get_object_or_404(CropCycle, id=crop_cycle_id, field__farm__owner=request.user)
        
        # Calculate overall growth stage
        if crop_cycle.planting_date:
            today = timezone.now().date()
            days_since_planting = (today - crop_cycle.planting_date).days
            if crop_cycle.crop.growing_period:
                growth_percentage = min(100, int((days_since_planting / crop_cycle.crop.growing_period) * 100))
            else:
                growth_percentage = 0
        else:
            growth_percentage = 0
        
        # Calculate upcoming harvests (within next 30 days)
        upcoming_harvests = []
        if crop_cycle.status == 'active' and crop_cycle.expected_harvest_date:
            today = timezone.now().date()
            days_until_harvest = (crop_cycle.expected_harvest_date - today).days
            if 0 <= days_until_harvest <= 30:
                upcoming_harvests.append({
                    'crop_name': crop_cycle.crop.name,
                    'field_name': crop_cycle.field.name,
                    'harvest_date': crop_cycle.expected_harvest_date,
                    'days_remaining': days_until_harvest
                })
        
        # Get recent activities for this crop cycle
        recent_activities = Activity.objects.filter(crop_cycle=crop_cycle).order_by('-actual_date', '-planned_date')[:5]
        
        # Get budget data for the dashboard
        # Get active budgets (current date falls between start_date and end_date)
        today = timezone.now().date()
        active_budgets = Budget.objects.filter(
            user=request.user,
            start_date__lte=today,
            end_date__gte=today
        )
        active_budgets_count = active_budgets.count()
        
        # Get recent budgets
        recent_budgets = Budget.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        # Calculate total planned income and expenses
        budget_totals = Budget.objects.filter(user=request.user).aggregate(
            total_planned_income=Sum('total_planned_income'),
            total_planned_expenses=Sum('total_planned_expenses')
        )
        
        total_planned_income = budget_totals['total_planned_income'] or 0
        total_planned_expenses = budget_totals['total_planned_expenses'] or 0
        
        context = {
            'crop_cycle': crop_cycle,
            'growth_percentage': growth_percentage,
            'upcoming_harvests': upcoming_harvests,
            'recent_activities': recent_activities,
            # Budget data
            'active_budgets_count': active_budgets_count,
            'recent_budgets': recent_budgets,
            'total_planned_income': total_planned_income,
            'total_planned_expenses': total_planned_expenses,
        }
        
        return render(request, 'farms/crop_dashboard.html', context)
    else:
        # Get user's farms
        farms = Farm.objects.filter(owner=request.user)
        
        # Count total crops planted
        total_crops = CropCycle.objects.filter(
            field__farm__owner=request.user,
            status__in=['planned', 'active']
        ).values('crop').distinct().count()
        
        # Get crop distribution
        crop_distribution = CropCycle.objects.filter(
            field__farm__owner=request.user,
            status__in=['planned', 'active']
        ).values('crop__name').annotate(
            total_area=Sum('field__size')
        ).order_by('-total_area')[:4]  # Top 4 crops by area
        
        # Calculate expected yields
        expected_yield = CropCycle.objects.filter(
            field__farm__owner=request.user,
            status__in=['planned', 'active']
        ).aggregate(total=Sum('expected_yield_kg'))['total'] or 0
        
        # Calculate total area under cultivation
        total_area = CropCycle.objects.filter(
            field__farm__owner=request.user,
            status__in=['planned', 'active']
        ).aggregate(total=Sum('field__size'))['total'] or 0
        
        # Determine overall growth stage (simplified)
        now = timezone.now().date()
        active_cycles = CropCycle.objects.filter(
            field__farm__owner=request.user,
            status='active',
            planting_date__lte=now
        )
        
        growth_stage = 'No active crops'
        if active_cycles.exists():
            # Simple logic to determine average growth stage
            early_stage = active_cycles.filter(planting_date__gte=now-timedelta(days=30)).count()
            mid_stage = active_cycles.filter(planting_date__lt=now-timedelta(days=30), 
                                           planting_date__gte=now-timedelta(days=60)).count()
            late_stage = active_cycles.filter(planting_date__lt=now-timedelta(days=60)).count()
            
            if early_stage > mid_stage and early_stage > late_stage:
                growth_stage = 'Early'
            elif mid_stage > early_stage and mid_stage > late_stage:
                growth_stage = 'Mid'
            else:
                growth_stage = 'Late'
        
        # Get upcoming harvests
        upcoming_harvests = CropCycle.objects.filter(
            field__farm__owner=request.user,
            status='active',
            expected_harvest_date__gte=now,
            expected_harvest_date__lte=now+timedelta(days=30)
        ).select_related('crop', 'field')
        
        # Get active budgets (current date falls between start_date and end_date)
        active_budgets = Budget.objects.filter(
            user=request.user,
            start_date__lte=now,
            end_date__gte=now
        )
        active_budgets_count = active_budgets.count()
        
        # Get recent budgets
        recent_budgets = Budget.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        # Calculate total planned income and expenses
        budget_totals = Budget.objects.filter(user=request.user).aggregate(
            total_planned_income=Sum('total_planned_income'),
            total_planned_expenses=Sum('total_planned_expenses')
        )
        
        total_planned_income = budget_totals['total_planned_income'] or 0
        total_planned_expenses = budget_totals['total_planned_expenses'] or 0
        
        context = {
            'farms': farms,
            'total_crops': total_crops,
            'crop_distribution': crop_distribution,
            'expected_yield': expected_yield,
            'growth_stage': growth_stage,
            'upcoming_harvests': upcoming_harvests,
            'active_page': 'crops',
            # Budget data
            'active_budgets_count': active_budgets_count,
            'recent_budgets': recent_budgets,
            'total_planned_income': total_planned_income,
            'total_planned_expenses': total_planned_expenses,
        }
        
        return render(request, 'farms/crop_dashboard.html', context)