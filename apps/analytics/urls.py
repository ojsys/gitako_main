from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main analytics views
    path('', views.profitability_dashboard, name='profitability_dashboard'),
    path('crop-analysis/', views.crop_profitability_analysis, name='crop_profitability_analysis'),
    path('field-analysis/', views.field_profitability_analysis, name='field_profitability_analysis'),
    
    # Analysis management
    path('create/', views.create_profitability_analysis, name='create_profitability_analysis'),
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    
    # Reports
    path('reports/', views.profitability_reports, name='profitability_reports'),
    
    # AJAX endpoints
    path('get-field-data/', views.get_field_data, name='get_field_data'),
    path('update-alert/<int:alert_id>/', views.update_alert_status, name='update_alert_status'),
]