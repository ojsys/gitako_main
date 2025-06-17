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
    path('crop-dashboard/<int:crop_cycle_id>/', views.crop_dashboard, name='crop_dashboard_detail'), # Specific crop cycle dashboard

    # AJAX
    path('ajax/get_crop_varieties/', views.get_crop_varieties, name='get_crop_varieties'),
    path('ajax/get_farm_fields/', views.get_farm_fields, name='get_farm_fields'),
]