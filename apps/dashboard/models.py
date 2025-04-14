from django.db import models
from apps.accounts.models import User

class DashboardWidget(models.Model):
    """Model for customizable dashboard widgets"""
    WIDGET_TYPES = (
        ('weather', 'Weather'),
        ('tasks', 'Tasks'),
        ('crops', 'Crop Status'),
        ('analytics', 'Analytics'),
        ('market', 'Market Prices'),
        ('calendar', 'Calendar'),
    )
    
    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # Widget can be global or user-specific
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='widgets')
    is_global = models.BooleanField(default=False)
    
    # Widget settings stored as JSON
    settings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"{self.title} ({self.user.username})"
        return f"{self.title} (Global)"
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"


class UserDashboardLayout(models.Model):
    """Model to store user's dashboard layout preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_layout')
    layout = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Dashboard Layout"
