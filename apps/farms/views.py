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

# Inport forms
from apps.farms.forms import FarmSectionForm, FarmSectionFilterForm, CropCycleForm, CropCycleFilterForm, CropForm # Add CropForm


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
def crop_create(request):
    """View to create a new crop."""
    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES)
        if form.is_valid():
            crop = form.save(commit=False)
            # If you have a user associated with the crop, set it here
            # crop.user = request.user # Assuming your Crop model has a user field
            crop.save()
            messages.success(request, f'Crop "{crop.name}" created successfully.')
            return redirect('farms:crop_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CropForm()
    
    context = {
        'form': form,
        'active_page': 'crops',
        'title': 'Add New Crop'
    }
    return render(request, 'farms/crop_form.html', context)

@login_required
def crop_edit(request, crop_id):
    """View to edit an existing crop."""
    crop = get_object_or_404(Crop, id=crop_id)
    # Optional: Add a check here if crops are user-specific
    # if crop.user != request.user:
    #     messages.error(request, "You don't have permission to edit this crop.")
    #     return redirect('farms:crop_list')

    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, f'Crop "{crop.name}" updated successfully.')
            return redirect('farms:crop_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CropForm(instance=crop)
    
    context = {
        'form': form,
        'crop': crop,
        'active_page': 'crops',
        'title': f'Edit Crop: {crop.name}'
    }
    return render(request, 'farms/crop_form.html', context)

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
            # start_date__lte=now,
            # end_date__gte=now
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



@login_required
def field_list(request):
    """View to display all fields/farm sections"""
    # Get user's farms
    farms = Farm.objects.filter(owner=request.user)
    
    # Get all fields for the user's farms
    fields = FarmSection.objects.filter(
        farm__owner=request.user,
        is_active=True
    ).select_related('farm').order_by('farm__name', 'name')
    
    # Filter by farm if provided
    farm_filter = request.GET.get('farm')
    if farm_filter:
        fields = fields.filter(farm__id=farm_filter)
    
    # Calculate totals
    total_fields = fields.count()
    total_area = fields.aggregate(total=Sum('size'))['total'] or 0
    
    # Get active crop cycles count per field
    fields_with_cycles = fields.annotate(
        active_cycles=Count('crop_cycles', filter=Q(crop_cycles__status__in=['planned', 'active']))
    )
    
    context = {
        'fields': fields_with_cycles,
        'farms': farms,
        'total_fields': total_fields,
        'total_area': total_area,
        'farm_filter': farm_filter,
        'active_page': 'fields'
    }
    
    return render(request, 'farms/field_list.html', context)

@login_required
def field_detail(request, field_id):
    """View to display details of a specific field"""
    field = get_object_or_404(FarmSection, id=field_id, farm__owner=request.user)
    
    # Get crop cycles for this field
    crop_cycles = CropCycle.objects.filter(field=field).select_related('crop', 'crop_variety')
    
    # Active crop cycles
    active_cycles = crop_cycles.filter(status__in=['planned', 'active'])
    
    # Historical crop cycles
    historical_cycles = crop_cycles.filter(status__in=['harvested', 'failed']).order_by('-planting_date')
    
    # Get soil tests for this field
    soil_tests = field.soil_tests.all().order_by('-test_date')[:5]
    
    context = {
        'field': field,
        'active_cycles': active_cycles,
        'historical_cycles': historical_cycles,
        'soil_tests': soil_tests,
        'active_page': 'fields'
    }
    
    return render(request, 'farms/field_detail.html', context)

@login_required
def field_create(request):
    """View to create a new field"""
    # Get user's farms
    farms = Farm.objects.filter(owner=request.user)
    
    if request.method == 'POST':
        form = FarmSectionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            field = form.save()
            messages.success(request, f'Field "{field.name}" has been created successfully.')
            return redirect('farms:field_detail', field_id=field.id)
    else:
        form = FarmSectionForm(user=request.user)
    
    context = {
        'form': form,
        'farms': farms,
        'active_page': 'fields'
    }
    
    return render(request, 'farms/field_form.html', context)

@login_required
def field_edit(request, field_id):
    """View to edit a field"""
    field = get_object_or_404(FarmSection, id=field_id, farm__owner=request.user)
    
    if request.method == 'POST':
        form = FarmSectionForm(request.POST, request.FILES, instance=field, user=request.user)
        if form.is_valid():
            field = form.save()
            messages.success(request, f'Field "{field.name}" has been updated successfully.')
            return redirect('farms:field_detail', field_id=field.id)
    else:
        form = FarmSectionForm(instance=field, user=request.user)
    
    context = {
        'form': form,
        'field': field,
        'active_page': 'fields'
    }
    
    return render(request, 'farms/field_form.html', context)

@login_required
def field_delete(request, field_id):
    """View to delete a field"""
    field = get_object_or_404(FarmSection, id=field_id, farm__owner=request.user)
    
    if request.method == 'POST':
        field_name = field.name
        field.delete()
        messages.success(request, f'Field "{field_name}" has been deleted successfully.')
        return redirect('farms:field_list')
    
    context = {
        'field': field,
        'active_page': 'fields'
    }
    
    return render(request, 'farms/field_confirm_delete.html', context)

@login_required
def crop_cycle_create(request):
    """View to create a new crop cycle"""
    if request.method == 'POST':
        form = CropCycleForm(request.POST, user=request.user)
        if form.is_valid():
            crop_cycle = form.save()
            messages.success(request, f'Crop cycle for {crop_cycle.crop.name} has been created successfully.')
            return redirect('farms:crop_cycle_detail', cycle_id=crop_cycle.id)
    else:
        form = CropCycleForm(user=request.user)
        
        # Pre-select field if provided in URL
        field_id = request.GET.get('field')
        if field_id:
            try:
                field = FarmSection.objects.get(id=field_id, farm__owner=request.user)
                form.fields['field'].initial = field
            except FarmSection.DoesNotExist:
                pass
    
    context = {
        'form': form,
        'active_page': 'crops'
    }
    
    return render(request, 'farms/crop_cycle_form.html', context)

@login_required
def crop_cycle_detail(request, cycle_id):
    """View to display details of a specific crop cycle"""
    crop_cycle = get_object_or_404(CropCycle, id=cycle_id, field__farm__owner=request.user)
    
    # Calculate growth progress
    if crop_cycle.planting_date and crop_cycle.expected_harvest_date:
        from django.utils import timezone
        today = timezone.now().date()
        total_days = (crop_cycle.expected_harvest_date - crop_cycle.planting_date).days
        days_elapsed = (today - crop_cycle.planting_date).days
        
        if total_days > 0:
            growth_percentage = min(100, max(0, int((days_elapsed / total_days) * 100)))
        else:
            growth_percentage = 0
    else:
        growth_percentage = 0
    
    # Get related activities (you'll need to import Activity model)
    try:
        from apps.activities.models import Activity
        activities = Activity.objects.filter(crop_cycle=crop_cycle).order_by('-actual_date', '-planned_date')
    except ImportError:
        activities = None
    
    context = {
        'crop_cycle': crop_cycle,
        'growth_percentage': growth_percentage,
        'activities': activities,
        'active_page': 'crops'
    }
    
    return render(request, 'farms/crop_cycle_detail.html', context)

@login_required
def crop_cycle_edit(request, cycle_id):
    """View to edit a crop cycle"""
    crop_cycle = get_object_or_404(CropCycle, id=cycle_id, field__farm__owner=request.user)
    
    if request.method == 'POST':
        form = CropCycleForm(request.POST, instance=crop_cycle, user=request.user)
        if form.is_valid():
            crop_cycle = form.save()
            messages.success(request, f'Crop cycle for {crop_cycle.crop.name} has been updated successfully.')
            return redirect('farms:crop_cycle_detail', cycle_id=crop_cycle.id)
    else:
        form = CropCycleForm(instance=crop_cycle, user=request.user)
    
    context = {
        'form': form,
        'crop_cycle': crop_cycle,
        'active_page': 'crops'
    }
    
    return render(request, 'farms/crop_cycle_form.html', context)

@login_required
def crop_cycle_delete(request, cycle_id):
    """View to delete a crop cycle"""
    crop_cycle = get_object_or_404(CropCycle, id=cycle_id, field__farm__owner=request.user)
    
    if request.method == 'POST':
        crop_name = f"{crop_cycle.crop.name} at {crop_cycle.field.name}"
        crop_cycle.delete()
        messages.success(request, f'Crop cycle "{crop_name}" has been deleted successfully.')
        return redirect('farms:crop_cycle_list')
    
    context = {
        'crop_cycle': crop_cycle,
        'active_page': 'crops'
    }
    
    return render(request, 'farms/crop_cycle_confirm_delete.html', context)

# AJAX views for dynamic form loading
@login_required
def get_crop_varieties(request):
    """AJAX view to get crop varieties based on selected crop"""
    crop_id = request.GET.get('crop_id')
    varieties = []
    
    if crop_id:
        try:
            crop = Crop.objects.get(id=crop_id)
            varieties = list(crop.varieties.values('id', 'name'))
        except Crop.DoesNotExist:
            pass
    
    return JsonResponse({'varieties': varieties})

@login_required
def get_farm_fields(request):
    """AJAX view to get fields based on selected farm"""
    farm_id = request.GET.get('farm_id')
    fields = []
    
    if farm_id:
        try:
            farm = Farm.objects.get(id=farm_id, owner=request.user)
            fields = list(farm.sections.filter(is_active=True).values('id', 'name', 'size'))
        except Farm.DoesNotExist:
            pass
    
    return JsonResponse({'fields': fields})
