from django.db import models
from django.conf import settings
from apps.farms.models import FarmSection, CropCycle

class Activity(models.Model):
    """Base model for all farm activities"""
    
    class ActivityType(models.TextChoices):
        LAND_CLEARING = 'land_clearing', 'Land Clearing'
        LAND_PREPARATION = 'land_preparation', 'Land Preparation'
        PLANTING = 'planting', 'Planting'
        FERTILIZER_APPLICATION = 'fertilizer', 'Fertilizer Application'
        PEST_CONTROL = 'pest_control', 'Pest Control'
        WEED_CONTROL = 'weed_control', 'Weed Control'
        IRRIGATION = 'irrigation', 'Irrigation'
        HARVESTING = 'harvesting', 'Harvesting'
        OTHER = 'other', 'Other'
    
    field = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='activities')
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    
    # Scheduling
    planned_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # General information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Cost tracking
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Weather conditions
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weather_notes = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_activities')
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.title}"
    
    class Meta:
        ordering = ['-planned_date', '-created_at']
        verbose_name_plural = "Activities"
    
    @property
    def total_cost(self):
        return self.labor_cost + self.material_cost + self.other_cost

class ActivityImage(models.Model):
    """Images associated with farm activities"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='activity_images/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.activity.title}"

class PlantingActivity(models.Model):
    """Extended details for planting activities"""
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, primary_key=True)
    seed_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    seed_unit = models.CharField(max_length=50)  # kg, bags, etc.
    planting_method = models.CharField(max_length=100, blank=True)
    spacing = models.CharField(max_length=100, blank=True)  # e.g., "30cm x 30cm"
    
    def __str__(self):
        return f"Planting details for {self.activity.title}"

class FertilizerActivity(models.Model):
    """Extended details for fertilizer application activities"""
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, primary_key=True)
    fertilizer_type = models.CharField(max_length=100)
    application_method = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)  # kg, bags, liters, etc.
    
    def __str__(self):
        return f"Fertilizer details for {self.activity.title}"

class PestControlActivity(models.Model):
    """Extended details for pest control activities"""
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, primary_key=True)
    product_name = models.CharField(max_length=100)
    target_pest = models.CharField(max_length=100, blank=True)
    application_method = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)  # liters, kg, etc.
    
    def __str__(self):
        return f"Pest control details for {self.activity.title}"

class IrrigationActivity(models.Model):
    """Extended details for irrigation activities"""
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, primary_key=True)
    irrigation_method = models.CharField(max_length=100)
    water_source = models.CharField(max_length=100, blank=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    water_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    water_unit = models.CharField(max_length=50, blank=True)  # liters, gallons, etc.
    
    def __str__(self):
        return f"Irrigation details for {self.activity.title}"

class HarvestActivity(models.Model):
    """Extended details for harvesting activities"""
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, primary_key=True)
    yield_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    yield_unit = models.CharField(max_length=50)  # kg, tons, bags, etc.
    quality_grade = models.CharField(max_length=50, blank=True)
    moisture_content = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Harvest details for {self.activity.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update crop cycle with actual yield and harvest date
        if self.activity.crop_cycle:
            crop_cycle = self.activity.crop_cycle
            
            # Convert yield to kg if needed
            yield_kg = self.yield_quantity
            if self.yield_unit.lower() != 'kg':
                # Basic conversion - in a real app, this would be more sophisticated
                if self.yield_unit.lower() == 'ton' or self.yield_unit.lower() == 'tons':
                    yield_kg = self.yield_quantity * 1000
            
            crop_cycle.actual_yield_kg = yield_kg
            crop_cycle.actual_harvest_date = self.activity.actual_date
            crop_cycle.status = 'harvested'
            crop_cycle.save()

class ActivityReminder(models.Model):
    """Reminders for scheduled activities"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='reminders')
    
    # Reminder timing
    reminder_date = models.DateField()
    reminder_time = models.TimeField(null=True, blank=True)
    
    # Notification settings
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=False)
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reminder for {self.activity.title} on {self.reminder_date}"
    
    class Meta:
        ordering = ['reminder_date', 'reminder_time']