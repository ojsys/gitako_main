from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q, F, Max, Min
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
from decimal import Decimal

from .models import (
    ProfitabilityAnalysis, CropProfitabilityTrend, FieldProfitabilityHistory,
    ProfitabilityBenchmark, ProfitabilityAlert
)
from apps.farms.models import Farm, FarmSection, Crop, CropCycle
from apps.activities.models import Activity
from apps.marketplace.models import ProduceProduct, Order, OrderItem


@login_required
def profitability_dashboard(request):
    """Comprehensive profitability dashboard"""
    user_farms = Farm.objects.filter(owner=request.user)
    
    # Get current year and season analyses
    current_year = timezone.now().year
    recent_analyses = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_date__year=current_year
    ).select_related('farm', 'field', 'crop')[:10]
    
    # Overall farm profitability
    total_profit = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_date__year=current_year
    ).aggregate(
        total_revenue=Sum('total_revenue'),
        total_costs=Sum('total_costs'),
        net_profit=Sum('net_profit')
    )
    
    # Most profitable crops
    profitable_crops = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_type='crop',
        analysis_date__year=current_year
    ).values('crop__name').annotate(
        total_profit=Sum('net_profit'),
        avg_margin=Avg('profit_margin'),
        total_yield=Sum('total_yield')
    ).order_by('-total_profit')[:5]
    
    # Least profitable crops (need attention)
    loss_making_crops = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_type='crop',
        net_profit__lt=0,
        analysis_date__year=current_year
    ).values('crop__name').annotate(
        total_loss=Sum('net_profit'),
        avg_margin=Avg('profit_margin')
    ).order_by('total_loss')[:3]
    
    # Field performance
    field_performance = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_type='field',
        analysis_date__year=current_year
    ).select_related('farm_section').order_by('-profit_margin')[:5]
    
    # Monthly profit trends
    monthly_trends = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_date__year=current_year
    ).extra(
        select={'month': "date_trunc('month', analysis_date)"}
    ).values('month').annotate(
        total_profit=Sum('net_profit'),
        total_revenue=Sum('total_revenue'),
        total_costs=Sum('total_costs')
    ).order_by('month')
    
    # Active alerts
    active_alerts = ProfitabilityAlert.objects.filter(
        user=request.user,
        is_active=True,
        is_acknowledged=False
    ).order_by('-severity', '-created_at')[:5]
    
    # Cost breakdown analysis
    cost_breakdown = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_date__year=current_year
    ).aggregate(
        total_seed_costs=Sum('seed_costs'),
        total_fertilizer_costs=Sum('fertilizer_costs'),
        total_pesticide_costs=Sum('pesticide_costs'),
        total_labor_costs=Sum('labor_costs'),
        total_equipment_costs=Sum('equipment_costs'),
        total_other_costs=Sum('other_costs')
    )
    
    context = {
        'recent_analyses': recent_analyses,
        'total_profit': total_profit,
        'profitable_crops': profitable_crops,
        'loss_making_crops': loss_making_crops,
        'field_performance': field_performance,
        'monthly_trends': json.dumps(list(monthly_trends), default=str),
        'active_alerts': active_alerts,
        'cost_breakdown': cost_breakdown,
        'user_farms': user_farms,
        'active_page': 'analytics'
    }
    
    return render(request, 'analytics/profitability_dashboard.html', context)


@login_required
def crop_profitability_analysis(request):
    """Detailed crop profitability analysis"""
    crops = Crop.objects.all()
    selected_crop_id = request.GET.get('crop')
    year = request.GET.get('year', timezone.now().year)
    
    crop_analyses = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_type='crop'
    )
    
    if selected_crop_id:
        crop_analyses = crop_analyses.filter(crop_id=selected_crop_id)
        selected_crop = get_object_or_404(Crop, id=selected_crop_id)
    else:
        selected_crop = None
    
    if year:
        crop_analyses = crop_analyses.filter(analysis_date__year=year)
    
    # Crop performance metrics
    crop_metrics = crop_analyses.aggregate(
        total_area=Sum('area_planted'),
        total_yield=Sum('total_yield'),
        avg_yield_per_ha=Avg('yield_per_hectare'),
        total_revenue=Sum('total_revenue'),
        total_costs=Sum('total_costs'),
        net_profit=Sum('net_profit'),
        avg_profit_margin=Avg('profit_margin'),
        avg_roi=Avg('roi')
    )
    
    # Historical trends
    historical_trends = CropProfitabilityTrend.objects.filter(
        user=request.user,
        crop_id=selected_crop_id if selected_crop_id else None
    ).order_by('year')
    
    # Benchmark comparison
    benchmarks = []
    if selected_crop:
        benchmarks = ProfitabilityBenchmark.objects.filter(
            crop=selected_crop,
            year=year
        )
    
    # Cost structure analysis
    cost_structure = crop_analyses.aggregate(
        seed_costs=Sum('seed_costs'),
        fertilizer_costs=Sum('fertilizer_costs'),
        pesticide_costs=Sum('pesticide_costs'),
        labor_costs=Sum('labor_costs'),
        equipment_costs=Sum('equipment_costs'),
        other_costs=Sum('other_costs')
    )
    
    context = {
        'crops': crops,
        'selected_crop': selected_crop,
        'year': year,
        'crop_analyses': crop_analyses,
        'crop_metrics': crop_metrics,
        'historical_trends': historical_trends,
        'benchmarks': benchmarks,
        'cost_structure': cost_structure,
        'active_page': 'analytics'
    }
    
    return render(request, 'analytics/crop_profitability_analysis.html', context)


@login_required
def field_profitability_analysis(request):
    """Detailed field profitability analysis"""
    user_farm_sections = FarmSection.objects.filter(farm__owner=request.user)
    selected_farm_section_id = request.GET.get('farm_section')
    year = request.GET.get('year', timezone.now().year)
    
    field_analyses = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_type='field'
    )
    
    if selected_farm_section_id:
        field_analyses = field_analyses.filter(farm_section_id=selected_farm_section_id)
        selected_farm_section = get_object_or_404(FarmSection, id=selected_farm_section_id, farm__owner=request.user)
    else:
        selected_farm_section = None
    
    if year:
        field_analyses = field_analyses.filter(analysis_date__year=year)
    
    # Field performance over time
    field_history = FieldProfitabilityHistory.objects.filter(
        user=request.user,
        farm_section_id=selected_farm_section_id if selected_farm_section_id else None
    ).select_related('crop_cycle', 'crop_cycle__crop')
    
    # Crop rotation impact analysis
    rotation_analysis = []
    if selected_farm_section:
        crop_cycles = CropCycle.objects.filter(
            field=selected_farm_section
        ).select_related('crop').order_by('planting_date')
        
        for cycle in crop_cycles:
            try:
                cycle_analysis = ProfitabilityAnalysis.objects.get(
                    farm_section=selected_farm_section,
                    crop_cycle=cycle
                )
                rotation_analysis.append({
                    'cycle': cycle,
                    'analysis': cycle_analysis
                })
            except ProfitabilityAnalysis.DoesNotExist:
                continue
    
    # Field metrics
    field_metrics = field_analyses.aggregate(
        avg_profit_per_ha=Avg('profit_per_hectare') if field_analyses else 0,
        total_profit=Sum('net_profit'),
        avg_yield_per_ha=Avg('yield_per_hectare'),
        avg_profit_margin=Avg('profit_margin')
    )
    
    context = {
        'user_farm_sections': user_farm_sections,
        'selected_farm_section': selected_farm_section,
        'year': year,
        'field_analyses': field_analyses,
        'field_history': field_history,
        'rotation_analysis': rotation_analysis,
        'field_metrics': field_metrics,
        'active_page': 'analytics'
    }
    
    return render(request, 'analytics/field_profitability_analysis.html', context)


@login_required
def create_profitability_analysis(request):
    """Create a new profitability analysis"""
    if request.method == 'POST':
        analysis_type = request.POST.get('analysis_type')
        
        # Create analysis based on type
        analysis = ProfitabilityAnalysis(
            user=request.user,
            analysis_type=analysis_type,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date')
        )
        
        # Set related objects based on type
        if analysis_type == 'farm':
            analysis.farm_id = request.POST.get('farm_id')
        elif analysis_type == 'field':
            analysis.farm_section_id = request.POST.get('farm_section_id')
            analysis.farm = FarmSection.objects.get(id=request.POST.get('farm_section_id')).farm
        elif analysis_type == 'crop':
            analysis.crop_id = request.POST.get('crop_id')
            if request.POST.get('farm_section_id'):
                analysis.farm_section_id = request.POST.get('farm_section_id')
                analysis.farm = FarmSection.objects.get(id=request.POST.get('farm_section_id')).farm
        
        # Calculate costs and revenues automatically
        analysis = calculate_analysis_metrics(analysis, request.POST)
        analysis.save()
        
        messages.success(request, 'Profitability analysis created successfully.')
        return redirect('analytics:profitability_dashboard')
    
    # Get form data
    user_farms = Farm.objects.filter(owner=request.user)
    user_farm_sections = FarmSection.objects.filter(farm__owner=request.user)
    crops = Crop.objects.all()
    
    context = {
        'user_farms': user_farms,
        'user_farm_sections': user_farm_sections,
        'crops': crops,
        'active_page': 'analytics'
    }
    
    return render(request, 'analytics/create_analysis.html', context)


@login_required
def analysis_detail(request, analysis_id):
    """Detailed view of a profitability analysis"""
    analysis = get_object_or_404(
        ProfitabilityAnalysis, 
        id=analysis_id, 
        user=request.user
    )
    
    # Get related activities and costs
    related_activities = []
    if analysis.farm_section:
        related_activities = Activity.objects.filter(
            field=analysis.farm_section,
            planned_date__range=[analysis.start_date, analysis.end_date]
        ).order_by('planned_date')
    
    # Get market data if available
    market_data = []
    if analysis.crop:
        # Get produce sales data
        produce_sales = OrderItem.objects.filter(
            order__seller=request.user,
            product__produceproduct__crop=analysis.crop,
            order__order_date__range=[analysis.start_date, analysis.end_date]
        ).select_related('order', 'product')
        
        market_data = produce_sales
    
    # Calculate cost per category as percentages
    total_costs = analysis.total_costs
    cost_percentages = {}
    if total_costs > 0:
        cost_percentages = {
            'seeds': (analysis.seed_costs / total_costs) * 100,
            'fertilizer': (analysis.fertilizer_costs / total_costs) * 100,
            'pesticides': (analysis.pesticide_costs / total_costs) * 100,
            'labor': (analysis.labor_costs / total_costs) * 100,
            'equipment': (analysis.equipment_costs / total_costs) * 100,
            'other': (analysis.other_costs / total_costs) * 100,
        }
    
    # Get benchmarks for comparison
    benchmarks = []
    if analysis.crop:
        benchmarks = ProfitabilityBenchmark.objects.filter(
            crop=analysis.crop,
            year=analysis.analysis_date.year
        )
    
    context = {
        'analysis': analysis,
        'related_activities': related_activities,
        'market_data': market_data,
        'cost_percentages': cost_percentages,
        'benchmarks': benchmarks,
        'active_page': 'analytics'
    }
    
    return render(request, 'analytics/analysis_detail.html', context)


def calculate_analysis_metrics(analysis, post_data):
    """Calculate analysis metrics from activities and market data"""
    
    # Revenue calculation
    revenue_sources = {
        'market_sales': Decimal(post_data.get('market_sales', 0)),
        'direct_sales': Decimal(post_data.get('direct_sales', 0)),
        'contract_sales': Decimal(post_data.get('contract_sales', 0)),
        'government_subsidy': Decimal(post_data.get('government_subsidy', 0))
    }
    
    analysis.market_sales = revenue_sources['market_sales']
    analysis.direct_sales = revenue_sources['direct_sales']
    analysis.contract_sales = revenue_sources['contract_sales']
    analysis.government_subsidy = revenue_sources['government_subsidy']
    analysis.total_revenue = sum(revenue_sources.values())
    
    # Cost calculation
    cost_categories = {
        'seed_costs': Decimal(post_data.get('seed_costs', 0)),
        'fertilizer_costs': Decimal(post_data.get('fertilizer_costs', 0)),
        'pesticide_costs': Decimal(post_data.get('pesticide_costs', 0)),
        'labor_costs': Decimal(post_data.get('labor_costs', 0)),
        'equipment_costs': Decimal(post_data.get('equipment_costs', 0)),
        'irrigation_costs': Decimal(post_data.get('irrigation_costs', 0)),
        'transportation_costs': Decimal(post_data.get('transportation_costs', 0)),
        'storage_costs': Decimal(post_data.get('storage_costs', 0)),
        'other_costs': Decimal(post_data.get('other_costs', 0))
    }
    
    for cost_type, amount in cost_categories.items():
        setattr(analysis, cost_type, amount)
    
    analysis.total_costs = sum(cost_categories.values())
    
    # Yield data
    analysis.total_yield = Decimal(post_data.get('total_yield', 0))
    analysis.area_planted = Decimal(post_data.get('area_planted', 0))
    
    return analysis


@login_required
def profitability_reports(request):
    """Comprehensive profitability reports"""
    year = request.GET.get('year', timezone.now().year)
    
    # Annual summary
    annual_summary = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_date__year=year
    ).aggregate(
        total_revenue=Sum('total_revenue'),
        total_costs=Sum('total_costs'),
        net_profit=Sum('net_profit'),
        total_area=Sum('area_planted'),
        total_yield=Sum('total_yield')
    )
    
    # Crop rankings
    crop_rankings = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_type='crop',
        analysis_date__year=year
    ).values('crop__name').annotate(
        total_profit=Sum('net_profit'),
        avg_margin=Avg('profit_margin'),
        total_area=Sum('area_planted'),
        avg_yield_per_ha=Avg('yield_per_hectare')
    ).order_by('-total_profit')
    
    # Field rankings
    field_rankings = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_type='field',
        analysis_date__year=year
    ).select_related('farm_section').annotate(
        profit_per_ha=F('net_profit') / F('area_planted')
    ).order_by('-profit_per_ha')
    
    # Cost efficiency analysis
    cost_efficiency = ProfitabilityAnalysis.objects.filter(
        user=request.user,
        analysis_date__year=year
    ).values('crop__name').annotate(
        avg_cost_per_ha=Avg(F('total_costs') / F('area_planted')),
        avg_revenue_per_ha=Avg(F('total_revenue') / F('area_planted')),
        efficiency_ratio=Avg(F('total_revenue') / F('total_costs'))
    ).order_by('-efficiency_ratio')
    
    context = {
        'year': year,
        'annual_summary': annual_summary,
        'crop_rankings': crop_rankings,
        'field_rankings': field_rankings,
        'cost_efficiency': cost_efficiency,
        'active_page': 'analytics'
    }
    
    return render(request, 'analytics/profitability_reports.html', context)


# AJAX Views
@login_required
def get_field_data(request):
    """AJAX endpoint to get farm section data for analysis"""
    farm_section_id = request.GET.get('farm_section_id')
    if farm_section_id:
        farm_section = get_object_or_404(FarmSection, id=farm_section_id, farm__owner=request.user)
        
        # Get recent crop cycles
        recent_cycles = CropCycle.objects.filter(
            field=farm_section
        ).select_related('crop').order_by('-planting_date')[:5]
        
        cycles_data = []
        for cycle in recent_cycles:
            cycles_data.append({
                'id': cycle.id,
                'crop_name': cycle.crop.name,
                'planting_date': cycle.planting_date.strftime('%Y-%m-%d'),
                'expected_harvest': cycle.expected_harvest_date.strftime('%Y-%m-%d') if cycle.expected_harvest_date else None
            })
        
        return JsonResponse({
            'success': True,
            'farm_section_name': farm_section.name,
            'area_hectares': float(farm_section.area_hectares),
            'recent_cycles': cycles_data
        })
    
    return JsonResponse({'success': False})


@login_required
def update_alert_status(request, alert_id):
    """AJAX endpoint to update alert status"""
    if request.method == 'POST':
        alert = get_object_or_404(ProfitabilityAlert, id=alert_id, user=request.user)
        action = request.POST.get('action')
        
        if action == 'acknowledge':
            alert.is_acknowledged = True
            alert.acknowledged_at = timezone.now()
        elif action == 'resolve':
            alert.is_active = False
            alert.resolved_at = timezone.now()
        
        alert.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Alert {action}d successfully'
        })
    
    return JsonResponse({'success': False})