from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from core.utils import get_file_path, generate_unique_slug


class Farm(models.Model):
    """Farm model representing a farming operation"""
    FARM_TYPES = (
        ('crop', 'Crop Farm'),
        ('livestock', 'Livestock Farm'),
        ('mixed', 'Mixed Farm'),
        ('aquaculture', 'Aquaculture'),
        ('poultry', 'Poultry'),
        ('orchard', 'Orchard'),
        ('vineyard', 'Vineyard'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    farm_type = models.CharField(max_length=20, choices=FARM_TYPES)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in acres")
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, 'name')
        super().save(*args, **kwargs)


class FarmSection(models.Model):
    """Sections or plots within a farm"""
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in acres")
    crop_type = models.CharField(max_length=255, blank=True, null=True)
    livestock_type = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.farm.name} - {self.name}"


class FarmEmployee(models.Model):
    """Employees working on a farm"""
    ROLE_CHOICES = (
        ('manager', 'Farm Manager'),
        ('worker', 'Farm Worker'),
        ('specialist', 'Specialist'),
        ('seasonal', 'Seasonal Worker'),
        ('other', 'Other'),
    )
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='employees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farm_employments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.farm.name} ({self.role})"


class Crop(models.Model):
    """Model representing a crop type"""
    name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    growing_season = models.CharField(max_length=100, blank=True)
    average_growing_period_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Growing conditions
    ideal_temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ideal_temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ideal_rainfall_min = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ideal_rainfall_max = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ideal_soil_ph_min = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ideal_soil_ph_max = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class CropVariety(models.Model):
    """Model representing a specific variety of a crop"""
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='varieties')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Variety characteristics
    maturity_days = models.PositiveIntegerField(null=True, blank=True)
    yield_potential = models.CharField(max_length=100, blank=True)
    disease_resistance = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.crop.name} - {self.name}"
    
    class Meta:
        verbose_name_plural = "Crop varieties"

class CropCycle(models.Model):
    """Model representing a crop growing cycle in a field"""
    field = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='crop_cycles')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='crop_cycles')
    crop_variety = models.ForeignKey(CropVariety, on_delete=models.SET_NULL, null=True, blank=True, related_name='crop_cycles')
    
    # Cycle dates
    planting_date = models.DateField()
    expected_harvest_date = models.DateField(null=True, blank=True)
    actual_harvest_date = models.DateField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('harvested', 'Harvested'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Yield information
    expected_yield_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_yield_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.crop.name} at {self.field.name} ({self.planting_date})"
    
    def save(self, *args, **kwargs):
        # Calculate expected harvest date if not provided
        if not self.expected_harvest_date and self.planting_date and self.crop.average_growing_period_days:
            from datetime import timedelta
            self.expected_harvest_date = self.planting_date + timedelta(days=self.crop.average_growing_period_days)
        
        # Call parent save first
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Auto-create calendar events for new crop cycles
        if is_new:
            self.create_automatic_calendar_events()
    
    def create_automatic_calendar_events(self):
        """Create automatic calendar events based on crop cycle"""
        from datetime import timedelta
        
        events_to_create = []
        
        # Planting event
        events_to_create.append({
            'event_type': 'planting',
            'title': f'Plant {self.crop.name}',
            'description': f'Plant {self.crop.name} in {self.field.name}',
            'start_date': self.planting_date,
            'priority': 'high'
        })
        
        # Calculate intermediate care events based on growing period
        if self.crop.average_growing_period_days:
            total_days = self.crop.average_growing_period_days
            
            # Fertilization (early growth - 2-3 weeks after planting)
            fertilizer_date = self.planting_date + timedelta(days=min(21, total_days // 4))
            events_to_create.append({
                'event_type': 'fertilizing',
                'title': f'Fertilize {self.crop.name}',
                'description': f'Apply fertilizer to {self.crop.name} in {self.field.name}',
                'start_date': fertilizer_date,
                'priority': 'medium'
            })
            
            # Weeding (mid growth)
            if total_days > 30:
                weeding_date = self.planting_date + timedelta(days=total_days // 2)
                events_to_create.append({
                    'event_type': 'weeding',
                    'title': f'Weed {self.crop.name} field',
                    'description': f'Remove weeds from {self.crop.name} in {self.field.name}',
                    'start_date': weeding_date,
                    'priority': 'medium'
                })
            
            # Pest inspection (3/4 through growth)
            if total_days > 45:
                pest_date = self.planting_date + timedelta(days=(total_days * 3) // 4)
                events_to_create.append({
                    'event_type': 'pest_control',
                    'title': f'Inspect {self.crop.name} for pests',
                    'description': f'Check {self.crop.name} in {self.field.name} for pest damage',
                    'start_date': pest_date,
                    'priority': 'medium'
                })
        
        # Harvest event
        if self.expected_harvest_date:
            events_to_create.append({
                'event_type': 'harvesting',
                'title': f'Harvest {self.crop.name}',
                'description': f'Harvest {self.crop.name} from {self.field.name}',
                'start_date': self.expected_harvest_date,
                'priority': 'high'
            })
        
        # Create the events
        for event_data in events_to_create:
            CropCalendar.objects.create(
                farm=self.field.farm,
                crop_cycle=self,
                created_by_id=self.field.farm.owner_id,  # Assuming the farm owner creates these
                **event_data
            )

class SoilTest(models.Model):
    """Model for soil test results"""
    field = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='soil_tests')
    test_date = models.DateField()
    
    # Test results
    ph = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nitrogen_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    phosphorus_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    potassium_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    organic_matter_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Additional nutrients
    calcium_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    magnesium_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sulfur_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    zinc_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    manganese_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    iron_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    copper_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    boron_ppm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Physical properties
    texture = models.CharField(max_length=100, blank=True)  # sandy, loamy, clay, etc.
    cec = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Cation Exchange Capacity
    
    # Test information
    laboratory = models.CharField(max_length=255, blank=True)
    test_method = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Soil Test for {self.field.name} on {self.test_date}"
    
    class Meta:
        ordering = ['-test_date']

class WeatherRecord(models.Model):
    """Model for weather data records"""
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='weather_records')
    date = models.DateField()
    
    # Temperature
    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Precipitation
    rainfall_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Other weather data
    humidity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_direction = models.CharField(max_length=50, blank=True)
    
    # Source of data
    SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('weather_station', 'Weather Station'),
        ('api', 'Weather API'),
    ]
    data_source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='api')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Weather for {self.farm.name} on {self.date}"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['farm', 'date']

class CropCalendar(models.Model):
    """Model for crop calendar events and scheduling"""
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='calendar_events')
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.CASCADE, related_name='calendar_events', null=True, blank=True)
    
    EVENT_TYPES = [
        ('planting', 'Planting'),
        ('fertilizing', 'Fertilizing'),
        ('weeding', 'Weeding'),
        ('watering', 'Watering'),
        ('pest_control', 'Pest Control'),
        ('pruning', 'Pruning'),
        ('harvesting', 'Harvesting'),
        ('soil_preparation', 'Soil Preparation'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Scheduling
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True)  # daily, weekly, monthly
    recurrence_interval = models.PositiveIntegerField(default=1)
    
    # Status
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Priority
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignment
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_calendar_events')
    
    # Weather dependency
    weather_dependent = models.BooleanField(default=False)
    min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    no_rain_required = models.BooleanField(default=False)
    
    # Cost estimation
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Completion tracking
    completion_date = models.DateField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_calendar_events')
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
    
    class Meta:
        ordering = ['start_date', 'priority']
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.status not in ['completed', 'cancelled'] and self.start_date < timezone.now().date():
            return True
        return False
    
    @property
    def duration_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 1

class SeasonalPlanning(models.Model):
    """Model for seasonal crop planning and rotation"""
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='seasonal_plans')
    field = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='seasonal_plans')
    
    season_year = models.PositiveIntegerField()
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
        ('wet', 'Wet Season'),
        ('dry', 'Dry Season'),
    ]
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    
    planned_crops = models.ManyToManyField(Crop, through='PlannedCropAllocation')
    
    # Planning details
    planning_notes = models.TextField(blank=True)
    soil_prep_required = models.BooleanField(default=True)
    irrigation_plan = models.TextField(blank=True)
    fertilization_plan = models.TextField(blank=True)
    
    # Budget planning
    estimated_total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seasonal_plans')
    
    def __str__(self):
        return f"{self.field.name} - {self.season} {self.season_year}"
    
    class Meta:
        ordering = ['-season_year', 'season']
        unique_together = ['field', 'season_year', 'season']

class PlannedCropAllocation(models.Model):
    """Through model for planned crop allocation in seasonal planning"""
    seasonal_plan = models.ForeignKey(SeasonalPlanning, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    crop_variety = models.ForeignKey(CropVariety, on_delete=models.CASCADE, null=True, blank=True)
    
    # Allocation details
    allocated_area = models.DecimalField(max_digits=10, decimal_places=2)  # in hectares
    expected_yield_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timing
    planned_planting_date = models.DateField()
    planned_harvest_date = models.DateField()
    
    # Economics
    estimated_cost_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.crop.name} - {self.allocated_area}ha"
    
    @property
    def expected_total_yield(self):
        if self.expected_yield_per_hectare:
            return self.allocated_area * self.expected_yield_per_hectare
        return None
    
    @property
    def estimated_total_cost(self):
        if self.estimated_cost_per_hectare:
            return self.allocated_area * self.estimated_cost_per_hectare
        return None
    
    @property
    def estimated_revenue(self):
        if self.expected_total_yield and self.expected_price_per_unit:
            return self.expected_total_yield * self.expected_price_per_unit
        return None

class CropRotationPlan(models.Model):
    """Model for crop rotation planning and recommendations"""
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='rotation_plans')
    field = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='rotation_plans')
    
    plan_name = models.CharField(max_length=255)
    rotation_cycle_years = models.PositiveIntegerField(default=3)
    
    # Rotation sequence
    year_1_crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='rotation_year_1')
    year_2_crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='rotation_year_2', null=True, blank=True)
    year_3_crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='rotation_year_3', null=True, blank=True)
    year_4_crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='rotation_year_4', null=True, blank=True)
    
    # Benefits and reasoning
    soil_health_benefits = models.TextField(blank=True)
    pest_management_benefits = models.TextField(blank=True)
    economic_benefits = models.TextField(blank=True)
    
    # Implementation
    start_year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rotation_plans')
    
    def __str__(self):
        return f"{self.plan_name} - {self.field.name}"
    
    def get_current_year_crop(self, current_year):
        """Get the crop that should be planted in the current year based on rotation cycle"""
        years_into_cycle = (current_year - self.start_year) % self.rotation_cycle_years
        
        if years_into_cycle == 0:
            return self.year_1_crop
        elif years_into_cycle == 1 and self.year_2_crop:
            return self.year_2_crop
        elif years_into_cycle == 2 and self.year_3_crop:
            return self.year_3_crop
        elif years_into_cycle == 3 and self.year_4_crop:
            return self.year_4_crop
        else:
            return self.year_1_crop