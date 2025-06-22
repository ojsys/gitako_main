from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from datetime import datetime
from apps.activities.models import Activity
from apps.inventory.models import InventoryItem, InventoryTransaction
from apps.farms.models import FarmSection


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class OfflineSyncView(View):
    """Handle offline data synchronization"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            sync_type = data.get('type')
            sync_data = data.get('data', [])
            
            results = []
            
            if sync_type == 'activities':
                results = self.sync_activities(request.user, sync_data)
            elif sync_type == 'inventory':
                results = self.sync_inventory(request.user, sync_data)
            elif sync_type == 'forms':
                results = self.sync_forms(request.user, sync_data)
            else:
                return JsonResponse({'error': 'Invalid sync type'}, status=400)
            
            return JsonResponse({
                'success': True,
                'synced_count': len(results),
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def sync_activities(self, user, activities_data):
        results = []
        
        for activity_data in activities_data:
            try:
                # Get or create the farm section
                farm_section = FarmSection.objects.get(
                    id=activity_data.get('farm_section_id'),
                    farm__owner=user
                )
                
                # Create the activity
                activity = Activity.objects.create(
                    field=farm_section,
                    activity_type=activity_data.get('activity_type'),
                    title=activity_data.get('title', ''),
                    description=activity_data.get('description', ''),
                    planned_date=datetime.fromisoformat(activity_data.get('planned_date')).date(),
                    actual_date=datetime.fromisoformat(activity_data.get('actual_date')).date() if activity_data.get('actual_date') else None,
                    status=activity_data.get('status', 'planned'),
                    cost=activity_data.get('cost', 0),
                    notes=activity_data.get('notes', '')
                )
                
                results.append({
                    'id': activity.id,
                    'offline_id': activity_data.get('offline_id'),
                    'status': 'synced'
                })
                
            except Exception as e:
                results.append({
                    'offline_id': activity_data.get('offline_id'),
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def sync_inventory(self, user, inventory_data):
        results = []
        
        for item_data in inventory_data:
            try:
                if item_data.get('type') == 'transaction':
                    # Sync inventory transaction
                    inventory_item = InventoryItem.objects.get(
                        id=item_data.get('inventory_item_id'),
                        user=user
                    )
                    
                    transaction = InventoryTransaction.objects.create(
                        inventory_item=inventory_item,
                        transaction_type=item_data.get('transaction_type'),
                        quantity=item_data.get('quantity'),
                        date=datetime.fromisoformat(item_data.get('date')).date(),
                        notes=item_data.get('notes', ''),
                        performed_by=user
                    )
                    
                    results.append({
                        'id': transaction.id,
                        'offline_id': item_data.get('offline_id'),
                        'status': 'synced'
                    })
                    
                elif item_data.get('type') == 'item':
                    # Sync new inventory item
                    inventory_item = InventoryItem.objects.create(
                        user=user,
                        name=item_data.get('name'),
                        item_type=item_data.get('item_type'),
                        description=item_data.get('description', ''),
                        quantity=item_data.get('quantity', 0),
                        unit=item_data.get('unit', ''),
                        status=item_data.get('status', 'available'),
                        storage_location=item_data.get('storage_location', ''),
                        acquisition_date=datetime.fromisoformat(item_data.get('acquisition_date')).date() if item_data.get('acquisition_date') else None
                    )
                    
                    results.append({
                        'id': inventory_item.id,
                        'offline_id': item_data.get('offline_id'),
                        'status': 'synced'
                    })
                
            except Exception as e:
                results.append({
                    'offline_id': item_data.get('offline_id'),
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def sync_forms(self, user, forms_data):
        results = []
        
        for form_data in forms_data:
            try:
                form_type = form_data.get('formType')
                data = form_data.get('data')
                
                if form_type == 'activity':
                    # Handle activity form
                    self.sync_activities(user, [data])
                    
                elif form_type == 'inventory':
                    # Handle inventory form
                    self.sync_inventory(user, [data])
                
                results.append({
                    'offline_id': form_data.get('offline_id'),
                    'status': 'synced'
                })
                
            except Exception as e:
                results.append({
                    'offline_id': form_data.get('offline_id'),
                    'status': 'error',
                    'error': str(e)
                })
        
        return results


@login_required
@require_http_methods(["GET"])
def get_offline_data(request):
    """Get essential data for offline use"""
    
    try:
        user = request.user
        
        # Get user's farms and sections
        from apps.farms.models import Farm, FarmSection, Crop
        farms = Farm.objects.filter(owner=user).values('id', 'name', 'location')
        farm_sections = FarmSection.objects.filter(farm__owner=user).values(
            'id', 'name', 'farm_id', 'area_hectares'
        )
        
        # Get crops
        crops = Crop.objects.all().values('id', 'name', 'category')
        
        # Get recent activities
        activities = Activity.objects.filter(
            field__farm__owner=user
        ).order_by('-created_at')[:50].values(
            'id', 'title', 'activity_type', 'planned_date', 'status'
        )
        
        # Get inventory items
        inventory_items = InventoryItem.objects.filter(user=user).values(
            'id', 'name', 'item_type', 'quantity', 'unit', 'status'
        )
        
        data = {
            'farms': list(farms),
            'farm_sections': list(farm_sections),
            'crops': list(crops),
            'activities': list(activities),
            'inventory_items': list(inventory_items),
            'timestamp': datetime.now().isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def handle_offline_form(request):
    """Handle form submissions that were stored offline"""
    
    try:
        data = json.loads(request.body)
        form_type = data.get('formType')
        form_data = data.get('data')
        
        if form_type == 'activity':
            # Create activity from offline form
            farm_section = FarmSection.objects.get(
                id=form_data.get('farm_section_id'),
                farm__owner=request.user
            )
            
            activity = Activity.objects.create(
                field=farm_section,
                activity_type=form_data.get('activity_type'),
                title=form_data.get('title', ''),
                description=form_data.get('description', ''),
                planned_date=datetime.fromisoformat(form_data.get('planned_date')).date(),
                cost=form_data.get('cost', 0),
                notes=form_data.get('notes', '')
            )
            
            return JsonResponse({
                'success': True,
                'id': activity.id,
                'message': 'Activity created successfully'
            })
            
        elif form_type == 'inventory_transaction':
            # Create inventory transaction from offline form
            inventory_item = InventoryItem.objects.get(
                id=form_data.get('inventory_item_id'),
                user=request.user
            )
            
            transaction = InventoryTransaction.objects.create(
                inventory_item=inventory_item,
                transaction_type=form_data.get('transaction_type'),
                quantity=form_data.get('quantity'),
                date=datetime.fromisoformat(form_data.get('date')).date(),
                notes=form_data.get('notes', ''),
                performed_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'id': transaction.id,
                'message': 'Transaction recorded successfully'
            })
        
        else:
            return JsonResponse({'error': 'Unknown form type'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def check_connection(request):
    """Simple endpoint to check if the app is online"""
    return JsonResponse({
        'online': True,
        'timestamp': datetime.now().isoformat(),
        'user': request.user.username
    })