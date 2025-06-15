from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('create/', views.activity_create, name='activity_create'),
    path('create/<int:crop_cycle_id>/', views.activity_create, name='activity_create_for_crop'),
    path('<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('<int:activity_id>/edit/', views.activity_edit, name='activity_edit'),
    path('<int:activity_id>/delete/', views.activity_delete, name='activity_delete'),
    path('<int:activity_id>/complete/', views.mark_activity_complete, name='mark_activity_complete'),
]