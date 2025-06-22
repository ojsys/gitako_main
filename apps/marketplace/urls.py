from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main marketplace views
    path('', views.marketplace_dashboard, name='marketplace_dashboard'),
    path('browse/', views.marketplace_browse, name='marketplace_browse'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # User's products
    path('my-products/', views.my_products, name='my_products'),
    path('create-input/', views.create_input_product, name='create_input_product'),
    path('create-produce/', views.create_produce_product, name='create_produce_product'),
    
    # Orders
    path('orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/create/<int:product_id>/', views.create_order, name='create_order'),
    
    # Analytics and reports
    path('analytics/', views.marketplace_analytics, name='marketplace_analytics'),
    
    # AJAX endpoints
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('search/', views.product_search, name='product_search'),
]