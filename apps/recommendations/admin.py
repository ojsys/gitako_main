from django.contrib import admin
from .models import (
    RecommendationEngine, CropRecommendation, WeatherRecommendation,
    PestDiseaseAlert, ResourceOptimization, MarketPricePrediction,
    RecommendationFeedback
)


@admin.register(RecommendationEngine)
class RecommendationEngineAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'recommendation_type', 'farm', 'priority', 
        'confidence_level', 'is_active', 'is_implemented', 'created_at'
    ]
    list_filter = [
        'recommendation_type', 'priority', 'confidence_level', 
        'is_active', 'is_implemented', 'created_at'
    ]
    search_fields = ['title', 'description', 'farm__name', 'user__username']
    readonly_fields = ['created_at', 'get_age_days']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recommendation_type', 'title', 'description', 'action_required')
        }),
        ('Targeting', {
            'fields': ('farm', 'crop', 'field', 'user')
        }),
        ('Priority & Confidence', {
            'fields': ('priority', 'confidence_level', 'valid_until')
        }),
        ('AI Model Information', {
            'fields': ('model_version', 'algorithm_used', 'data_points_used', 'accuracy_score'),
            'classes': ['collapse']
        }),
        ('Status Tracking', {
            'fields': ('is_active', 'is_implemented', 'implemented_at', 'feedback_rating', 'feedback_notes')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'get_age_days'),
            'classes': ['collapse']
        })
    )
    
    def get_age_days(self, obj):
        return f"{obj.get_age_days()} days"
    get_age_days.short_description = 'Age (days)'


@admin.register(CropRecommendation)
class CropRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'recommended_crop', 'farm', 'field', 'season', 
        'suitability_score', 'profit_potential', 'risk_level', 'created_at'
    ]
    list_filter = ['season', 'risk_level', 'confidence_level', 'competition_level']
    search_fields = ['recommended_crop__name', 'farm__name', 'field__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'field', 'recommended_crop', 'season')
        }),
        ('Recommendation Scores', {
            'fields': ('suitability_score', 'profit_potential', 'risk_level', 'confidence_level')
        }),
        ('Environmental Factors', {
            'fields': ('soil_compatibility', 'climate_compatibility', 'water_requirement_match')
        }),
        ('Market Factors', {
            'fields': ('market_demand_score', 'price_trend_score', 'competition_level')
        }),
        ('Timing', {
            'fields': ('optimal_planting_start', 'optimal_planting_end', 'expected_harvest_date')
        })
    )


@admin.register(WeatherRecommendation)
class WeatherRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'farm', 'weather_condition', 'temperature_range', 
        'precipitation_forecast', 'valid_from', 'valid_until'
    ]
    list_filter = ['weather_condition', 'weather_data_source', 'created_at']
    search_fields = ['farm__name', 'weather_condition']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'weather_condition', 'temperature_range', 'humidity_level', 'precipitation_forecast')
        }),
        ('Recommendations', {
            'fields': ('irrigation_advice', 'pest_risk_alert', 'harvest_timing_advice', 'field_work_recommendations')
        }),
        ('Data Source', {
            'fields': ('weather_data_source', 'forecast_accuracy')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        })
    )


@admin.register(PestDiseaseAlert)
class PestDiseaseAlertAdmin(admin.ModelAdmin):
    list_display = [
        'pest_or_disease_name', 'type', 'farm', 'crop', 
        'severity_level', 'probability_percentage', 'is_active', 'alert_date'
    ]
    list_filter = ['type', 'severity_level', 'is_active', 'prediction_model', 'alert_date']
    search_fields = ['pest_or_disease_name', 'farm__name', 'crop__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'crop', 'field', 'pest_or_disease_name', 'type')
        }),
        ('Risk Assessment', {
            'fields': ('severity_level', 'probability_percentage', 'confidence_score', 'risk_factors')
        }),
        ('Predictions', {
            'fields': ('expected_impact', 'expected_onset_date')
        }),
        ('Recommendations', {
            'fields': ('recommended_actions', 'treatment_options', 'prevention_measures', 'monitoring_schedule')
        }),
        ('AI Model', {
            'fields': ('prediction_model',),
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ('is_active', 'resolved_at')
        })
    )


@admin.register(ResourceOptimization)
class ResourceOptimizationAdmin(admin.ModelAdmin):
    list_display = [
        'resource_type', 'farm', 'current_cost', 'potential_savings', 
        'efficiency_improvement_percentage', 'confidence_level', 'created_at'
    ]
    list_filter = ['resource_type', 'confidence_level', 'created_at']
    search_fields = ['farm__name', 'optimization_method']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'resource_type', 'crop', 'field')
        }),
        ('Current Usage', {
            'fields': ('current_usage_amount', 'current_usage_unit', 'current_cost')
        }),
        ('Optimization Recommendations', {
            'fields': ('recommended_usage_amount', 'potential_savings', 'efficiency_improvement_percentage')
        }),
        ('Implementation', {
            'fields': ('optimization_method', 'implementation_timeline', 'required_investment', 'payback_period_days')
        }),
        ('Environmental Impact', {
            'fields': ('environmental_benefit', 'sustainability_score')
        }),
        ('Confidence', {
            'fields': ('confidence_level',)
        })
    )


@admin.register(MarketPricePrediction)
class MarketPricePredictionAdmin(admin.ModelAdmin):
    list_display = [
        'crop', 'region', 'current_price', 'predicted_price', 
        'price_change_percentage', 'recommended_action', 'prediction_date'
    ]
    list_filter = ['recommended_action', 'prediction_model', 'region', 'created_at']
    search_fields = ['crop__name', 'region']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('crop', 'region', 'price_unit')
        }),
        ('Price Data', {
            'fields': ('current_price', 'predicted_price', 'prediction_date', 'prediction_horizon_days')
        }),
        ('Market Factors', {
            'fields': ('supply_demand_ratio', 'seasonal_factor', 'weather_impact_factor')
        }),
        ('Recommendations', {
            'fields': ('recommended_action', 'optimal_selling_date')
        }),
        ('Model Metadata', {
            'fields': ('prediction_model', 'confidence_interval', 'accuracy_score'),
            'classes': ['collapse']
        })
    )
    
    def price_change_percentage(self, obj):
        return f"{obj.price_change_percentage():.1f}%"
    price_change_percentage.short_description = 'Price Change %'


@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'recommendation', 'user', 'usefulness_rating', 'accuracy_rating', 
        'implementation_difficulty', 'was_implemented', 'created_at'
    ]
    list_filter = [
        'usefulness_rating', 'accuracy_rating', 'implementation_difficulty', 
        'was_implemented', 'would_recommend_to_others', 'created_at'
    ]
    search_fields = ['recommendation__title', 'user__username', 'comments']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recommendation', 'user')
        }),
        ('Feedback Scores', {
            'fields': ('usefulness_rating', 'accuracy_rating', 'implementation_difficulty')
        }),
        ('Implementation', {
            'fields': ('was_implemented', 'outcome_description', 'actual_results')
        }),
        ('Additional Feedback', {
            'fields': ('comments', 'would_recommend_to_others')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
