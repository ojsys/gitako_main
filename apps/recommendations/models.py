from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json

User = get_user_model()


class RecommendationEngine(models.Model):
    RECOMMENDATION_TYPES = [
        ('crop_selection', 'Crop Selection'),
        ('planting_timing', 'Planting Timing'),
        ('weather_based', 'Weather Based'),
        ('pest_disease', 'Pest & Disease'),
        ('resource_optimization', 'Resource Optimization'),
        ('market_timing', 'Market Timing'),
        ('fertilizer', 'Fertilizer Application'),
        ('irrigation', 'Irrigation Schedule'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    action_required = models.TextField(blank=True)
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS, default='medium')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # AI model metadata
    model_version = models.CharField(max_length=50, default='v1.0')
    algorithm_used = models.CharField(max_length=100, blank=True)
    data_points_used = models.IntegerField(default=0)
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Targeting
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='ai_recommendations')
    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, null=True, blank=True)
    field = models.ForeignKey('farms.FarmSection', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    implemented_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    is_implemented = models.BooleanField(default=False)
    feedback_rating = models.IntegerField(null=True, blank=True, help_text="1-5 star rating from user")
    feedback_notes = models.TextField(blank=True)
    
    # Additional data storage
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farm', 'recommendation_type']),
            models.Index(fields=['created_at', 'is_active']),
            models.Index(fields=['priority', 'confidence_level']),
        ]
    
    def __str__(self):
        return f"{self.get_recommendation_type_display()}: {self.title}"
    
    def is_expired(self):
        if self.valid_until:
            return timezone.now() > self.valid_until
        return False
    
    def get_age_days(self):
        return (timezone.now() - self.created_at).days


class CropRecommendation(models.Model):
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE)
    field = models.ForeignKey('farms.FarmSection', on_delete=models.CASCADE, null=True, blank=True)
    recommended_crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE)
    season = models.CharField(max_length=20)
    
    # Recommendation scores
    suitability_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="0-100 suitability score")
    profit_potential = models.DecimalField(max_digits=12, decimal_places=2, help_text="Estimated profit per hectare")
    risk_level = models.CharField(max_length=10, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], default='medium')
    
    # Environmental factors
    soil_compatibility = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    climate_compatibility = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    water_requirement_match = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Market factors
    market_demand_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    price_trend_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    competition_level = models.CharField(max_length=10, choices=[
        ('low', 'Low Competition'),
        ('medium', 'Medium Competition'),
        ('high', 'High Competition'),
    ], default='medium')
    
    # Timing recommendations
    optimal_planting_start = models.DateField(null=True, blank=True)
    optimal_planting_end = models.DateField(null=True, blank=True)
    expected_harvest_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    confidence_level = models.CharField(max_length=10, choices=RecommendationEngine.CONFIDENCE_LEVELS, default='medium')
    
    class Meta:
        ordering = ['-suitability_score']
        unique_together = ['farm', 'field', 'recommended_crop', 'season']
    
    def __str__(self):
        field_name = f" in {self.field.name}" if self.field else ""
        return f"{self.recommended_crop.name} for {self.farm.name}{field_name} ({self.season})"


class WeatherRecommendation(models.Model):
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE)
    weather_condition = models.CharField(max_length=50)
    temperature_range = models.CharField(max_length=20, blank=True)
    humidity_level = models.CharField(max_length=20, blank=True)
    precipitation_forecast = models.CharField(max_length=50, blank=True)
    
    # Recommendations
    irrigation_advice = models.TextField(blank=True)
    pest_risk_alert = models.TextField(blank=True)
    harvest_timing_advice = models.TextField(blank=True)
    field_work_recommendations = models.TextField(blank=True)
    
    # Weather data source
    weather_data_source = models.CharField(max_length=100, default='OpenWeatherMap')
    forecast_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Weather advice for {self.farm.name} - {self.weather_condition}"


class PestDiseaseAlert(models.Model):
    SEVERITY_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical'),
    ]
    
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE)
    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, null=True, blank=True)
    field = models.ForeignKey('farms.FarmSection', on_delete=models.CASCADE, null=True, blank=True)
    
    pest_or_disease_name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=[
        ('pest', 'Pest'),
        ('disease', 'Disease'),
        ('weed', 'Weed'),
    ])
    
    severity_level = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    risk_factors = models.JSONField(default=list, help_text="List of contributing risk factors")
    
    # Predictions
    probability_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expected_impact = models.TextField()
    recommended_actions = models.TextField()
    treatment_options = models.JSONField(default=list)
    
    # Prevention
    prevention_measures = models.TextField(blank=True)
    monitoring_schedule = models.TextField(blank=True)
    
    alert_date = models.DateTimeField(auto_now_add=True)
    expected_onset_date = models.DateField(null=True, blank=True)
    
    # AI model info
    prediction_model = models.CharField(max_length=50, default='pest_disease_v1')
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4)
    
    is_active = models.BooleanField(default=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-alert_date']
        indexes = [
            models.Index(fields=['farm', 'severity_level']),
            models.Index(fields=['crop', 'type']),
        ]
    
    def __str__(self):
        return f"{self.pest_or_disease_name} alert for {self.farm.name}"


class ResourceOptimization(models.Model):
    RESOURCE_TYPES = [
        ('water', 'Water/Irrigation'),
        ('fertilizer', 'Fertilizer'),
        ('seeds', 'Seeds'),
        ('labor', 'Labor'),
        ('equipment', 'Equipment'),
        ('energy', 'Energy'),
    ]
    
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, null=True, blank=True)
    field = models.ForeignKey('farms.FarmSection', on_delete=models.CASCADE, null=True, blank=True)
    
    # Current usage analysis
    current_usage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_usage_unit = models.CharField(max_length=20)
    current_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Optimization recommendations
    recommended_usage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    potential_savings = models.DecimalField(max_digits=12, decimal_places=2)
    efficiency_improvement_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Implementation details
    optimization_method = models.TextField()
    implementation_timeline = models.CharField(max_length=100)
    required_investment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payback_period_days = models.IntegerField(null=True, blank=True)
    
    # Environmental impact
    environmental_benefit = models.TextField(blank=True)
    sustainability_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    confidence_level = models.CharField(max_length=10, choices=RecommendationEngine.CONFIDENCE_LEVELS)
    
    class Meta:
        ordering = ['-potential_savings']
    
    def __str__(self):
        return f"{self.get_resource_type_display()} optimization for {self.farm.name}"


class MarketPricePrediction(models.Model):
    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE)
    region = models.CharField(max_length=100, default='Local Market')
    
    # Price data
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=20, default='per kg')
    
    # Prediction timeframe
    prediction_date = models.DateField()
    prediction_horizon_days = models.IntegerField(default=30)
    
    # Market factors
    supply_demand_ratio = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    seasonal_factor = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    weather_impact_factor = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Recommendations
    recommended_action = models.CharField(max_length=20, choices=[
        ('hold', 'Hold/Wait'),
        ('sell_now', 'Sell Now'),
        ('sell_later', 'Sell Later'),
        ('store', 'Store for Better Price'),
    ])
    optimal_selling_date = models.DateField(null=True, blank=True)
    
    # Model metadata
    prediction_model = models.CharField(max_length=50, default='price_forecast_v1')
    confidence_interval = models.CharField(max_length=20, blank=True)
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prediction_date']
        unique_together = ['crop', 'region', 'prediction_date']
    
    def __str__(self):
        return f"{self.crop.name} price prediction for {self.prediction_date}"
    
    def price_change_percentage(self):
        if self.current_price > 0:
            return ((self.predicted_price - self.current_price) / self.current_price) * 100
        return 0


class RecommendationFeedback(models.Model):
    recommendation = models.ForeignKey(RecommendationEngine, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Feedback scores
    usefulness_rating = models.IntegerField(choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)])
    accuracy_rating = models.IntegerField(choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)])
    implementation_difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('difficult', 'Difficult'),
    ])
    
    # Outcomes
    was_implemented = models.BooleanField()
    outcome_description = models.TextField(blank=True)
    actual_results = models.TextField(blank=True)
    
    # Additional feedback
    comments = models.TextField(blank=True)
    would_recommend_to_others = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recommendation', 'user']
    
    def __str__(self):
        return f"Feedback for {self.recommendation.title} by {self.user.username}"