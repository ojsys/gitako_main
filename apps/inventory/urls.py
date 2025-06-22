from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Main inventory views
    path('', views.inventory_dashboard, name='inventory_dashboard'),
    path('items/', views.inventory_list, name='inventory_list'),
    path('items/create/', views.inventory_item_create, name='inventory_item_create'),
    path('items/<int:item_id>/', views.inventory_item_detail, name='inventory_item_detail'),
    path('items/<int:item_id>/edit/', views.inventory_item_edit, name='inventory_item_edit'),
    
    # Specialized item details
    path('items/<int:item_id>/equipment/', views.equipment_create, name='equipment_create'),
    path('items/<int:item_id>/input/', views.farm_input_create, name='farm_input_create'),
    
    # Transactions
    path('items/<int:item_id>/transaction/', views.transaction_create, name='transaction_create'),
    path('items/<int:item_id>/quick-transaction/', views.quick_transaction, name='quick_transaction'),
    
    # Maintenance
    path('equipment/<int:equipment_id>/maintenance/', views.maintenance_record_create, name='maintenance_record_create'),
    
    # Reports and analytics
    path('reports/', views.inventory_reports, name='inventory_reports'),
    
    # AJAX endpoints
    path('search/', views.inventory_search, name='inventory_search'),
]