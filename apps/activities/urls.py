from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    # Main activity management
    path('', views.activity_list, name='activity_list'),
    path('create/', views.activity_create, name='activity_create'),
    path('create/<int:crop_cycle_id>/', views.activity_create, name='activity_create_for_crop'),
    path('<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('<int:activity_id>/edit/', views.activity_edit, name='activity_edit'),
    path('<int:activity_id>/delete/', views.activity_delete, name='activity_delete'),
    path('<int:activity_id>/complete/', views.mark_activity_complete, name='mark_activity_complete'),
    
    # Enhanced farm records views
    path('dashboard/', views.farm_records_dashboard, name='farm_records_dashboard'),
    path('analytics/', views.activity_analytics, name='activity_analytics'),
    path('calendar/', views.activity_calendar, name='activity_calendar'),
    
    # Specialized records
    path('planting/', views.planting_records, name='planting_records'),
    path('harvest/', views.harvest_records, name='harvest_records'),
    path('weather/', views.weather_records, name='weather_records'),
    
    # AJAX endpoints
    path('<int:activity_id>/add-image/', views.add_activity_image, name='add_activity_image'),
    path('<int:activity_id>/quick-complete/', views.activity_quick_complete, name='activity_quick_complete'),
    path('ajax/field-crop-cycles/', views.get_field_crop_cycles, name='get_field_crop_cycles'),
]