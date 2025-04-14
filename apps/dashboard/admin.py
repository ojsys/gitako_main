from django.contrib import admin
from .models import DashboardWidget, UserDashboardLayout

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'user', 'is_global', 'is_active', 'order')
    list_filter = ('widget_type', 'is_global', 'is_active')
    search_fields = ('title', 'user__username')
    list_editable = ('is_active', 'order')

@admin.register(UserDashboardLayout)
class UserDashboardLayoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    search_fields = ('user__username',)
