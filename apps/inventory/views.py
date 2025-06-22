from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q, F
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    InventoryItem, Equipment, FarmInput, InventoryTransaction, MaintenanceRecord
)
from .forms import (
    InventoryItemForm, EquipmentForm, FarmInputForm, InventoryTransactionForm, MaintenanceRecordForm
)
from apps.farms.models import Farm

@login_required
def inventory_dashboard(request):
    """Comprehensive inventory management dashboard"""
    user_inventory = InventoryItem.objects.filter(user=request.user)
    
    # Inventory statistics
    total_items = user_inventory.count()
    low_stock_items = user_inventory.filter(quantity__lte=5).count()
    expired_items = FarmInput.objects.filter(
        inventory_item__user=request.user,
        expiry_date__lt=timezone.now().date()
    ).count()
    
    # Items by type
    items_by_type = user_inventory.values('item_type').annotate(
        count=Count('id'),
        total_value=Sum('equipment__current_value') + Sum('farminput__purchase_price')
    ).order_by('-count')
    
    # Recent transactions
    recent_transactions = InventoryTransaction.objects.filter(
        inventory_item__user=request.user
    ).select_related('inventory_item').order_by('-created_at')[:10]
    
    # Equipment needing maintenance
    equipment_maintenance = Equipment.objects.filter(
        inventory_item__user=request.user,
        next_maintenance_date__lte=timezone.now().date() + timedelta(days=30)
    ).select_related('inventory_item')
    
    # Low stock alerts
    low_stock_alerts = user_inventory.filter(
        quantity__lte=5,
        status__in=['available', 'in_use']
    ).order_by('quantity')[:5]
    
    # Expired/expiring items
    expiring_items = FarmInput.objects.filter(
        inventory_item__user=request.user,
        expiry_date__gte=timezone.now().date(),
        expiry_date__lte=timezone.now().date() + timedelta(days=30)
    ).select_related('inventory_item').order_by('expiry_date')
    
    # Monthly transactions summary
    this_month = timezone.now().date().replace(day=1)
    monthly_transactions = InventoryTransaction.objects.filter(
        inventory_item__user=request.user,
        date__gte=this_month
    ).values('transaction_type').annotate(
        count=Count('id'),
        total_value=Sum('total_price')
    )
    
    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'expired_items': expired_items,
        'items_by_type': items_by_type,
        'recent_transactions': recent_transactions,
        'equipment_maintenance': equipment_maintenance,
        'low_stock_alerts': low_stock_alerts,
        'expiring_items': expiring_items,
        'monthly_transactions': monthly_transactions,
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/inventory_dashboard.html', context)

@login_required
def inventory_list(request):
    """List all inventory items with filtering and search"""
    items = InventoryItem.objects.filter(user=request.user).select_related(
        'equipment', 'farminput'
    ).order_by('-created_at')
    
    # Apply filters
    item_type = request.GET.get('type')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if item_type:
        items = items.filter(item_type=item_type)
    
    if status:
        items = items.filter(status=status)
    
    if search:
        items = items.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(storage_location__icontains=search)
        )
    
    # Get filter options
    item_types = InventoryItem.ItemType.choices
    status_choices = InventoryItem.STATUS_CHOICES
    
    context = {
        'items': items,
        'item_types': item_types,
        'status_choices': status_choices,
        'current_filters': {
            'type': item_type,
            'status': status,
            'search': search
        },
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def inventory_item_detail(request, item_id):
    """Detailed view of an inventory item"""
    item = get_object_or_404(InventoryItem, id=item_id, user=request.user)
    
    # Get related data based on item type
    equipment_detail = None
    input_detail = None
    
    if item.item_type == 'equipment':
        try:
            equipment_detail = Equipment.objects.get(inventory_item=item)
        except Equipment.DoesNotExist:
            pass
    
    elif item.item_type == 'input':
        try:
            input_detail = FarmInput.objects.get(inventory_item=item)
        except FarmInput.DoesNotExist:
            pass
    
    # Get transaction history
    transactions = InventoryTransaction.objects.filter(
        inventory_item=item
    ).order_by('-date')
    
    # Get maintenance records for equipment
    maintenance_records = []
    if equipment_detail:
        maintenance_records = MaintenanceRecord.objects.filter(
            equipment=equipment_detail
        ).order_by('-maintenance_date')
    
    context = {
        'item': item,
        'equipment_detail': equipment_detail,
        'input_detail': input_detail,
        'transactions': transactions,
        'maintenance_records': maintenance_records,
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/inventory_item_detail.html', context)

@login_required
def inventory_item_create(request):
    """Create a new inventory item"""
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            
            messages.success(request, f'Inventory item "{item.name}" created successfully.')
            return redirect('inventory:inventory_item_detail', item_id=item.id)
    else:
        form = InventoryItemForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Add New Inventory Item',
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/inventory_item_form.html', context)

@login_required
def inventory_item_edit(request, item_id):
    """Edit an existing inventory item"""
    item = get_object_or_404(InventoryItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inventory item "{item.name}" updated successfully.')
            return redirect('inventory:inventory_item_detail', item_id=item.id)
    else:
        form = InventoryItemForm(instance=item, user=request.user)
    
    context = {
        'form': form,
        'item': item,
        'title': f'Edit {item.name}',
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/inventory_item_form.html', context)

@login_required
def equipment_create(request, item_id):
    """Add equipment details to an inventory item"""
    item = get_object_or_404(InventoryItem, id=item_id, user=request.user, item_type='equipment')
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.inventory_item = item
            equipment.save()
            messages.success(request, f'Equipment details added for "{item.name}".')
            return redirect('inventory:inventory_item_detail', item_id=item.id)
    else:
        form = EquipmentForm()
    
    context = {
        'form': form,
        'item': item,
        'title': f'Add Equipment Details - {item.name}',
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/equipment_form.html', context)

@login_required
def farm_input_create(request, item_id):
    """Add farm input details to an inventory item"""
    item = get_object_or_404(InventoryItem, id=item_id, user=request.user, item_type='input')
    
    if request.method == 'POST':
        form = FarmInputForm(request.POST)
        if form.is_valid():
            farm_input = form.save(commit=False)
            farm_input.inventory_item = item
            farm_input.save()
            messages.success(request, f'Farm input details added for "{item.name}".')
            return redirect('inventory:inventory_item_detail', item_id=item.id)
    else:
        form = FarmInputForm()
    
    context = {
        'form': form,
        'item': item,
        'title': f'Add Input Details - {item.name}',
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/farm_input_form.html', context)

@login_required
def transaction_create(request, item_id):
    """Create a new inventory transaction"""
    item = get_object_or_404(InventoryItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.inventory_item = item
            transaction.performed_by = request.user
            transaction.save()
            
            messages.success(request, f'Transaction recorded for "{item.name}".')
            return redirect('inventory:inventory_item_detail', item_id=item.id)
    else:
        form = InventoryTransactionForm(user=request.user)
    
    context = {
        'form': form,
        'item': item,
        'title': f'Record Transaction - {item.name}',
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/transaction_form.html', context)

@login_required
def maintenance_record_create(request, equipment_id):
    """Create a maintenance record for equipment"""
    equipment = get_object_or_404(
        Equipment, 
        id=equipment_id, 
        inventory_item__user=request.user
    )
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.equipment = equipment
            maintenance.recorded_by = request.user
            maintenance.save()
            
            messages.success(request, f'Maintenance record added for "{equipment.inventory_item.name}".')
            return redirect('inventory:inventory_item_detail', item_id=equipment.inventory_item.id)
    else:
        form = MaintenanceRecordForm()
    
    context = {
        'form': form,
        'equipment': equipment,
        'title': f'Record Maintenance - {equipment.inventory_item.name}',
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/maintenance_form.html', context)

@login_required
def inventory_reports(request):
    """Inventory reports and analytics"""
    user_inventory = InventoryItem.objects.filter(user=request.user)
    
    # Inventory value by type
    inventory_value = user_inventory.values('item_type').annotate(
        count=Count('id'),
        total_equipment_value=Sum('equipment__current_value'),
        total_input_cost=Sum('farminput__purchase_price')
    )
    
    # Transaction trends (last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    transaction_trends = InventoryTransaction.objects.filter(
        inventory_item__user=request.user,
        date__gte=six_months_ago
    ).extra(
        select={'month': "date_trunc('month', date)"}
    ).values('month', 'transaction_type').annotate(
        count=Count('id'),
        total_value=Sum('total_price')
    ).order_by('month')
    
    # Equipment utilization
    equipment_usage = Equipment.objects.filter(
        inventory_item__user=request.user
    ).annotate(
        maintenance_count=Count('maintenance_records'),
        days_since_last_maintenance=timezone.now().date() - F('last_maintenance_date')
    )
    
    # Input consumption patterns
    input_consumption = InventoryTransaction.objects.filter(
        inventory_item__user=request.user,
        transaction_type='usage',
        inventory_item__item_type='input'
    ).values(
        'inventory_item__farminput__input_category'
    ).annotate(
        total_consumed=Sum('quantity'),
        total_cost=Sum('total_price')
    ).order_by('-total_consumed')
    
    context = {
        'inventory_value': inventory_value,
        'transaction_trends': json.dumps(list(transaction_trends), default=str),
        'equipment_usage': equipment_usage,
        'input_consumption': input_consumption,
        'active_page': 'inventory'
    }
    
    return render(request, 'inventory/inventory_reports.html', context)

# AJAX Views
@login_required
def quick_transaction(request, item_id):
    """AJAX view for quick inventory transactions"""
    if request.method == 'POST':
        item = get_object_or_404(InventoryItem, id=item_id, user=request.user)
        
        transaction_type = request.POST.get('transaction_type')
        quantity = float(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')
        
        # Create transaction
        transaction = InventoryTransaction.objects.create(
            inventory_item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            date=timezone.now().date(),
            notes=notes,
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Transaction recorded successfully.',
            'new_quantity': float(item.quantity)
        })
    
    return JsonResponse({'success': False})

@login_required
def inventory_search(request):
    """AJAX search for inventory items"""
    query = request.GET.get('q', '')
    if len(query) >= 2:
        items = InventoryItem.objects.filter(
            user=request.user,
            name__icontains=query
        ).values('id', 'name', 'item_type', 'quantity', 'unit')[:10]
        
        return JsonResponse({
            'success': True,
            'items': list(items)
        })
    
    return JsonResponse({'success': False, 'items': []})
