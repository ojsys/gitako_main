# Add these URL patterns to your farms app's urls.py

from django.urls import path
from . import views

app_name = 'farms'

urlpatterns = [
    # Existing URLs...
    path('crops/', views.crop_list, name='crop_list'),
    path('crops/add/', views.crop_create, name='crop_create'), # New
    path('crops/<int:crop_id>/', views.crop_detail, name='crop_detail'),
    path('crops/<int:crop_id>/edit/', views.crop_edit, name='crop_edit'), # New
    
    path('fields/', views.field_list, name='field_list'),
    path('fields/add/', views.field_create, name='field_create'),
    path('fields/<int:field_id>/', views.field_detail, name='field_detail'),
    path('fields/<int:field_id>/edit/', views.field_edit, name='field_edit'),
    path('fields/<int:field_id>/delete/', views.field_delete, name='field_delete'),

    path('crop-cycles/', views.crop_cycle_list, name='crop_cycle_list'),
    path('crop-cycles/add/', views.crop_cycle_create, name='crop_cycle_create'),
    path('crop-cycles/add/for-field/<int:field_id>/', views.crop_cycle_create, name='crop_cycle_create_for_field'),
    path('crop-cycles/<int:pk>/', views.crop_cycle_detail, name='crop_cycle_detail'),
    path('crop-cycles/<int:pk>/edit/', views.crop_cycle_edit, name='crop_cycle_edit'),
    path('crop-cycles/<int:pk>/delete/', views.crop_cycle_delete, name='crop_cycle_delete'),
    path('crop-dashboard/', views.crop_dashboard, name='crop_dashboard'), # Overview dashboard
    

    # Crop Calendar URLs
    path('calendar/', views.crop_calendar_view, name='crop_calendar'),
    path('calendar/event/add/', views.crop_calendar_create, name='crop_calendar_create'),
    path('calendar/event/<int:event_id>/edit/', views.crop_calendar_edit, name='crop_calendar_edit'),
    path('calendar/event/<int:event_id>/delete/', views.crop_calendar_delete, name='crop_calendar_delete'),
    path('calendar/event/<int:event_id>/complete/', views.crop_calendar_complete, name='crop_calendar_complete'),
    
    # Excel Template and Bulk Upload URLs
    path('calendar/download-template/', views.crop_calendar_download_template, name='crop_calendar_download_template'),
    path('calendar/bulk-upload/', views.crop_calendar_bulk_upload, name='crop_calendar_bulk_upload'),
    
    # Seasonal Planning URLs
    path('planning/', views.seasonal_planning_list, name='seasonal_planning_list'),
    path('planning/add/', views.seasonal_planning_create, name='seasonal_planning_create'),
    path('planning/<int:plan_id>/', views.seasonal_planning_detail, name='seasonal_planning_detail'),
    
    # Crop Rotation URLs
    path('rotation/', views.crop_rotation_list, name='crop_rotation_list'),
    path('rotation/add/', views.crop_rotation_create, name='crop_rotation_create'),
    path('rotation/recommendations/', views.crop_rotation_recommendations, name='crop_rotation_recommendations'),

    # Analytics URLs
    path('analytics/', views.yield_analytics, name='yield_analytics'),
    path('analytics/crop/<int:crop_id>/', views.crop_performance_detail, name='crop_performance_detail'),

    # AJAX
    path('ajax/get_crop_varieties/', views.get_crop_varieties, name='get_crop_varieties'),
    path('ajax/get_farm_fields/', views.get_farm_fields, name='get_farm_fields'),
]