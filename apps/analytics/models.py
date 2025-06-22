from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from apps.farms.models import Farm, FarmSection, Crop, CropCycle
from apps.activities.models import Activity

User = get_user_model()


class ProfitabilityAnalysis(models.Model):
    """Model to track profitability analysis for crops and fields"""
    
    ANALYSIS_TYPE_CHOICES = [
        ('crop', 'Crop Analysis'),
        ('field', 'Field Analysis'),
        ('season', 'Seasonal Analysis'),
        ('farm', 'Farm Analysis')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES)
    analysis_date = models.DateField(default=timezone.now)
    
    # Related objects
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, null=True, blank=True)
    farm_section = models.ForeignKey(FarmSection, on_delete=models.CASCADE, null=True, blank=True)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True)
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.CASCADE, null=True, blank=True)
    
    # Analysis period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Financial metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    roi = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Return on Investment
    
    # Yield metrics
    total_yield = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yield_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    area_planted = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Cost breakdown
    seed_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fertilizer_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pesticide_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labor_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    equipment_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    irrigation_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transportation_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    storage_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Revenue breakdown
    market_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    direct_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contract_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    government_subsidy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes and recommendations
    notes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-analysis_date']
        verbose_name = 'Profitability Analysis'
        verbose_name_plural = 'Profitability Analyses'
    
    def __str__(self):
        if self.analysis_type == 'crop' and self.crop:
            return f"{self.crop.name} Analysis - {self.analysis_date}"
        elif self.analysis_type == 'field' and self.farm_section:
            return f"{self.farm_section.name} Analysis - {self.analysis_date}"
        elif self.analysis_type == 'farm' and self.farm:
            return f"{self.farm.name} Analysis - {self.analysis_date}"
        return f"{self.get_analysis_type_display()} - {self.analysis_date}"
    
    def calculate_metrics(self):
        """Calculate all financial metrics"""
        self.gross_profit = self.total_revenue - self.total_costs
        self.net_profit = self.gross_profit  # In simple case, same as gross profit
        
        if self.total_costs > 0:
            self.roi = (self.net_profit / self.total_costs) * 100
        
        if self.total_revenue > 0:
            self.profit_margin = (self.net_profit / self.total_revenue) * 100
        
        if self.area_planted > 0:
            self.yield_per_hectare = self.total_yield / self.area_planted
    
    def save(self, *args, **kwargs):
        self.calculate_metrics()
        super().save(*args, **kwargs)


class CropProfitabilityTrend(models.Model):
    """Model to track profitability trends over time"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    year = models.IntegerField()
    season = models.CharField(max_length=20, blank=True)
    
    # Aggregated metrics
    total_area_planted = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_yield = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_yield_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_profit_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Market data
    average_market_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_volatility = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-season']
        unique_together = ['user', 'crop', 'year', 'season']
    
    def __str__(self):
        return f"{self.crop.name} - {self.year} {self.season}"


class FieldProfitabilityHistory(models.Model):
    """Model to track field profitability history"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    farm_section = models.ForeignKey(FarmSection, on_delete=models.CASCADE)
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.CASCADE)
    
    # Cycle-specific metrics
    cycle_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cycle_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cycle_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cycle_yield = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Soil and environmental factors
    soil_quality_score = models.IntegerField(default=0, help_text="1-10 scale")
    weather_impact_score = models.IntegerField(default=0, help_text="1-10 scale")
    pest_disease_impact = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage loss
    
    # Efficiency metrics
    cost_per_hectare = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    revenue_per_hectare = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    profit_per_hectare = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.farm_section.name} - {self.crop_cycle.crop.name} ({self.crop_cycle.planting_date})"


class ProfitabilityBenchmark(models.Model):
    """Model to store industry benchmarks and comparisons"""
    
    BENCHMARK_TYPE_CHOICES = [
        ('regional', 'Regional Average'),
        ('national', 'National Average'),
        ('industry', 'Industry Standard'),
        ('best_practice', 'Best Practice')
    ]
    
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    benchmark_type = models.CharField(max_length=20, choices=BENCHMARK_TYPE_CHOICES)
    region = models.CharField(max_length=100, blank=True)
    year = models.IntegerField()
    
    # Benchmark metrics
    avg_yield_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_revenue_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_cost_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_profit_per_hectare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Cost breakdown benchmarks
    avg_seed_cost_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # % of total cost
    avg_fertilizer_cost_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_labor_cost_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year']
        unique_together = ['crop', 'benchmark_type', 'region', 'year']
    
    def __str__(self):
        return f"{self.crop.name} - {self.get_benchmark_type_display()} ({self.year})"


class ProfitabilityAlert(models.Model):
    """Model to track profitability alerts and notifications"""
    
    ALERT_TYPE_CHOICES = [
        ('low_profit', 'Low Profit Margin'),
        ('high_cost', 'High Cost Alert'),
        ('poor_yield', 'Poor Yield Performance'),
        ('market_opportunity', 'Market Opportunity'),
        ('benchmark_below', 'Below Benchmark'),
        ('trend_decline', 'Declining Trend')
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    
    # Related objects
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, null=True, blank=True)
    farm_section = models.ForeignKey(FarmSection, on_delete=models.CASCADE, null=True, blank=True)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True)
    analysis = models.ForeignKey(ProfitabilityAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    
    # Alert details
    message = models.TextField()
    recommendation = models.TextField(blank=True)
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Alert status
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.severity.title()}"