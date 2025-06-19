from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core site URLs
    path('core', include('core.urls')),
    
    # Dashboard URLs
    path('dashboard/', include('apps.dashboard.urls')),
    
    # App URLs
    path('accounts/', include('apps.accounts.urls')),
    path('farms/', include('apps.farms.urls')),
    path('activities/', include('apps.activities.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('', include('apps.site_config.urls')), # For Home
    path('financials/', include('apps.financials.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    
    # API URLs
    path('api/v1/', include('api.v1.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)