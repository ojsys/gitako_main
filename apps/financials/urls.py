from django.urls import path
from . import views

app_name = 'financials'

urlpatterns = [
    path('', views.budget_dashboard, name='budget_dashboard'),
    # Budget URLs
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.budget_create, name='budget_create'),
    path('budgets/<int:budget_id>/', views.budget_detail, name='budget_detail'),
    path('budgets/<int:budget_id>/update/', views.budget_update, name='budget_update'),
    path('budgets/<int:budget_id>/delete/', views.budget_delete, name='budget_delete'),
    
    # Budget Item URLs
    path('budgets/<int:budget_id>/items/create/', views.budget_item_create, name='budget_item_create'),
    path('budget-items/<int:item_id>/update/', views.budget_item_update, name='budget_item_update'),
    path('budget-items/<int:item_id>/delete/', views.budget_item_delete, name='budget_item_delete'),
    
]