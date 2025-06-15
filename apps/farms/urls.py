from django.urls import path
from . import views

app_name = 'farms'

urlpatterns = [
    # Crop management URLs
    path('crops/', views.crop_dashboard, name='crop_dashboard'),
    path('crops/list/', views.crop_list, name='crop_list'),
    path('crops/<int:crop_id>/', views.crop_detail, name='crop_detail'),
    path('crops/cycles/', views.crop_cycle_list, name='crop_cycle_list'),
]