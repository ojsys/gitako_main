from django.db import models
from django.conf import settings
from apps.farms.models import Farm, FarmSection, Crop, CropCycle

class Recommendation(models.Model):
    """Base model for all recommendations"""
    
    class RecommendationType(models.TextChoices):
        CROP = 'crop', 'Crop Recommendation'
        FERTILIZER = 'fertilizer', 'Fertilizer Recommendation'
        PEST_CONTROL = 'pest_control', 'Pest Control Recommendation'
        IRRIGATION = 'irrigation', 'Irrigation Recommendation'
        MARKET = 'market', 'Market Recommendation'
        GENERAL = 'general', 'General Recommendation'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='recommendations', null=True, blank=True)
    field = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='recommendations', null=True, blank=True)
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.CASCADE, related_name='recommendations', null=True, blank=True)
    
    recommendation_type = models.CharField(max_length=20, choices=RecommendationType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Priority and status
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Validity period
    valid_from = models.DateField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)
    
    # User feedback
    user_feedback = models.TextField(blank=True)
    user_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 rating
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.valid_until:
            return today <= self.valid_until
        return True

class CropRecommendation(models.Model):
    """Extended details for crop recommendations"""
    recommendation = models.OneToOneField(Recommendation, on_delete=models.CASCADE, primary_key=True)
    
    # Recommended crops
    recommended_crops = models.ManyToManyField(Crop, through='RecommendedCrop')
    
    # Factors considered
    soil_factors = models.TextField(blank=True)
    climate_factors = models.TextField(blank=True)
    market_factors = models.TextField(blank=True)
    
    def __str__(self):
        return f"Crop recommendation: {self.recommendation.title}"

class RecommendedCrop(models.Model):
    """Junction model for crop recommendations with additional data"""
    crop_recommendation = models.ForeignKey(CropRecommendation, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    
    # Recommendation details
    suitability_score = models.DecimalField(max_digits=5, decimal_places=2)  # 0-100 score
    expected_yield = models.CharField(max_length=100, blank=True)
    expected_profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    planting_window_start = models.DateField(null=True, blank=True)
    planting_window_end = models.DateField(null=True, blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.crop.name} for {self.crop_recommendation.recommendation.title}"
    
    class Meta:
        ordering = ['-suitability_score']

class FertilizerRecommendation(models.Model):
    """Extended details for fertilizer recommendations"""
    recommendation = models.OneToOneField(Recommendation, on_delete=models.CASCADE, primary_key=True)
    
    # Nutrient recommendations
    nitrogen_kg_per_ha = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    phosphorus_kg_per_ha = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    potassium_kg_per_ha = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Application details
    recommended_products = models.TextField(blank=True)
    application_timing = models.CharField(max_length=255, blank=True)
    application_method = models.CharField(max_length=255, blank=True)
    
    # Basis for recommendation
    soil_test_based = models.BooleanField(default=False)
    crop_requirement_based = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Fertilizer recommendation: {self.recommendation.title}"

class PestControlRecommendation(models.Model):
    """Extended details for pest control recommendations"""
    recommendation = models.OneToOneField(Recommendation, on_delete=models.CASCADE, primary_key=True)
    
    # Pest information
    target_pest = models.CharField(max_length=255)
    pest_pressure = models.CharField(max_length=50, blank=True)  # low, medium, high
    
    # Treatment recommendations
    recommended_products = models.TextField(blank=True)
    application_timing = models.CharField(max_length=255, blank=True)
    application_method = models.CharField(max_length=255, blank=True)
    
    # Integrated pest management
    cultural_controls = models.TextField(blank=True)
    biological_controls = models.TextField(blank=True)
    preventive_measures = models.TextField(blank=True)
    
    def __str__(self):
        return f"Pest control recommendation: {self.recommendation.title}"

class IrrigationRecommendation(models.Model):
    """Extended details for irrigation recommendations"""
    recommendation = models.OneToOneField(Recommendation, on_delete=models.CASCADE, primary_key=True)
    
    # Water requirements
    water_requirement_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    frequency_days = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Irrigation details
    recommended_method = models.CharField(max_length=100, blank=True)
    irrigation_duration = models.CharField(max_length=100, blank=True)
    
    # Factors considered
    soil_moisture = models.CharField(max_length=50, blank=True)
    weather_forecast = models.TextField(blank=True)
    crop_stage = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Irrigation recommendation: {self.recommendation.title}"

class MarketRecommendation(models.Model):
    """Extended details for market recommendations"""
    recommendation = models.OneToOneField(Recommendation, on_delete=models.CASCADE, primary_key=True)
    
    # Market information
    market_trends = models.TextField(blank=True)
    price_forecast = models.TextField(blank=True)
    
    # Selling recommendations
    recommended_timing = models.CharField(max_length=255, blank=True)
    recommended_markets = models.TextField(blank=True)
    potential_buyers = models.TextField(blank=True)
    
    # Price information
    current_price_range = models.CharField(max_length=100, blank=True)
    expected_price_range = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Market recommendation: {self.recommendation.title}"
