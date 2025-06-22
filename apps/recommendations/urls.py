from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Dashboard
    path('', views.recommendations_dashboard, name='dashboard'),
    
    # Main recommendation views
    path('generate/', views.generate_recommendations, name='generate'),
    path('list/', views.recommendations_list, name='list'),
    path('detail/<int:recommendation_id>/', views.recommendation_detail, name='detail'),
    
    # Specialized views
    path('pest-alerts/', views.pest_disease_alerts, name='pest_alerts'),
    path('market-predictions/', views.market_predictions, name='market_predictions'),
    path('resource-optimizations/', views.resource_optimizations, name='resource_optimizations'),
    
    # AJAX endpoints
    path('ajax/action/', views.ajax_recommendation_action, name='ajax_action'),
]