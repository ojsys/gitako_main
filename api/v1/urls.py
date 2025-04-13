from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Web and shared endpoints
    path('accounts/', include('apps.accounts.urls')),
    path('farms/', include('apps.farms.urls')),
    path('activities/', include('apps.activities.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('financials/', include('apps.financials.urls')),
    
    # Mobile-specific authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Mobile-specific endpoints
    path('mobile/', include('api.v1.mobile.urls')),
]