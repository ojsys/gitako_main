from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('sync/', views.OfflineSyncView.as_view(), name='offline_sync'),
    path('offline-data/', views.get_offline_data, name='get_offline_data'),
    path('forms/submit/', views.handle_offline_form, name='handle_offline_form'),
    path('check-connection/', views.check_connection, name='check_connection'),
]