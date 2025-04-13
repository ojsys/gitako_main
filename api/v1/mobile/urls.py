from django.urls import path
from . import views

urlpatterns = [
    path('config/', views.MobileConfigView.as_view(), name='mobile_config'),
    path('register-device/', views.RegisterDeviceView.as_view(), name='register_device'),
    path('sync/', views.DataSyncView.as_view(), name='data_sync'),
]