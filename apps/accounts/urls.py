from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # API endpoints
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    
    # Web views
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Password reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]