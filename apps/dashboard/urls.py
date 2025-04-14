from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('settings/update/', views.update_settings, name='update_settings'),
    path('export-data/', views.export_data, name='export_data'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('save-layout/', views.save_layout, name='save_layout'),
]