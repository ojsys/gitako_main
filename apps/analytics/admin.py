from django.contrib import admin
from .models import (
    ProfitabilityAnalysis, CropProfitabilityTrend, FieldProfitabilityHistory,
    ProfitabilityBenchmark, ProfitabilityAlert
)


@admin.register(ProfitabilityAnalysis)
class ProfitabilityAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'analysis_type', 'analysis_date', 'crop', 'field', 'net_profit', 'profit_margin'
    ]
    list_filter = ['analysis_type', 'analysis_date', 'crop', 'user']
    search_fields = ['user__username', 'crop__name', 'field__name']
    readonly_fields = ['gross_profit', 'net_profit', 'profit_margin', 'roi', 'yield_per_hectare']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'analysis_type', 'analysis_date', 'farm', 'field', 'crop', 'crop_cycle')
        }),
        ('Analysis Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Financial Metrics', {
            'fields': ('total_revenue', 'total_costs', 'gross_profit', 'net_profit', 'profit_margin', 'roi')
        }),
        ('Yield Information', {
            'fields': ('total_yield', 'area_planted', 'yield_per_hectare')
        }),
        ('Cost Breakdown', {
            'fields': ('seed_costs', 'fertilizer_costs', 'pesticide_costs', 'labor_costs', 
                      'equipment_costs', 'irrigation_costs', 'transportation_costs', 'storage_costs', 'other_costs')
        }),
        ('Revenue Breakdown', {
            'fields': ('market_sales', 'direct_sales', 'contract_sales', 'government_subsidy')
        }),
        ('Notes', {
            'fields': ('notes', 'recommendations')
        })
    )


@admin.register(CropProfitabilityTrend)
class CropProfitabilityTrendAdmin(admin.ModelAdmin):
    list_display = ['user', 'crop', 'year', 'season', 'net_profit', 'average_yield_per_hectare']
    list_filter = ['year', 'season', 'crop', 'user']
    search_fields = ['user__username', 'crop__name']


@admin.register(FieldProfitabilityHistory)
class FieldProfitabilityHistoryAdmin(admin.ModelAdmin):
    list_display = ['field', 'crop_cycle', 'cycle_profit', 'profit_per_hectare', 'cycle_yield']
    list_filter = ['field__farm', 'crop_cycle__crop']
    search_fields = ['field__name', 'crop_cycle__crop__name']


@admin.register(ProfitabilityBenchmark)
class ProfitabilityBenchmarkAdmin(admin.ModelAdmin):
    list_display = ['crop', 'benchmark_type', 'region', 'year', 'avg_profit_per_hectare']
    list_filter = ['benchmark_type', 'year', 'crop']
    search_fields = ['crop__name', 'region']


@admin.register(ProfitabilityAlert)
class ProfitabilityAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert_type', 'severity', 'is_active', 'is_acknowledged', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_active', 'is_acknowledged']
    search_fields = ['user__username', 'message']
    actions = ['mark_as_acknowledged', 'mark_as_resolved']
    
    def mark_as_acknowledged(self, request, queryset):
        queryset.update(is_acknowledged=True)
    mark_as_acknowledged.short_description = "Mark selected alerts as acknowledged"
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_active=False)
    mark_as_resolved.short_description = "Mark selected alerts as resolved"