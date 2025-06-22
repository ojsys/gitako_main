from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator

from apps.farms.models import Farm
from .models import (
    RecommendationEngine, CropRecommendation, WeatherRecommendation,
    PestDiseaseAlert, ResourceOptimization, MarketPricePrediction,
    RecommendationFeedback
)
from .ai_algorithms import run_ai_recommendations_for_farm


@login_required
def recommendations_dashboard(request):
    """Main recommendations dashboard"""
    
    # Get user's farms
    user_farms = Farm.objects.filter(owner=request.user)
    
    if not user_farms.exists():
        messages.warning(request, "You need to create a farm first to get AI recommendations.")
        return redirect('farms:farm_list')
    
    # Get selected farm (default to first farm)
    farm_id = request.GET.get('farm_id')
    if farm_id:
        selected_farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
    else:
        selected_farm = user_farms.first()
    
    # Get active recommendations for the farm
    active_recommendations = RecommendationEngine.objects.filter(
        farm=selected_farm,
        is_active=True,
        user=request.user
    ).order_by('-priority', '-created_at')
    
    # Get recommendations by type
    recommendations_by_type = {
        'crop_selection': active_recommendations.filter(recommendation_type='crop_selection')[:3],
        'weather_based': active_recommendations.filter(recommendation_type='weather_based')[:3],
        'pest_disease': active_recommendations.filter(recommendation_type='pest_disease')[:3],
        'resource_optimization': active_recommendations.filter(recommendation_type='resource_optimization')[:3],
        'market_timing': active_recommendations.filter(recommendation_type='market_timing')[:3],
    }
    
    # Get urgent recommendations
    urgent_recommendations = active_recommendations.filter(priority='urgent')[:5]
    
    # Get recent pest/disease alerts
    recent_alerts = PestDiseaseAlert.objects.filter(
        farm=selected_farm,
        is_active=True
    ).order_by('-alert_date')[:5]
    
    # Get weather recommendations for next 7 days
    weather_recommendations = WeatherRecommendation.objects.filter(
        farm=selected_farm,
        valid_until__gte=timezone.now()
    ).order_by('valid_from')[:7]
    
    # Calculate statistics
    stats = {
        'total_active': active_recommendations.count(),
        'high_priority': active_recommendations.filter(priority__in=['high', 'urgent']).count(),
        'implemented': RecommendationEngine.objects.filter(
            farm=selected_farm,
            user=request.user,
            is_implemented=True
        ).count(),
        'avg_rating': RecommendationFeedback.objects.filter(
            recommendation__farm=selected_farm
        ).aggregate(avg_rating=Avg('usefulness_rating'))['avg_rating'] or 0
    }
    
    context = {
        'selected_farm': selected_farm,
        'user_farms': user_farms,
        'recommendations_by_type': recommendations_by_type,
        'urgent_recommendations': urgent_recommendations,
        'recent_alerts': recent_alerts,
        'weather_recommendations': weather_recommendations,
        'stats': stats,
        'page_title': 'AI Recommendations Dashboard'
    }
    
    return render(request, 'recommendations/dashboard.html', context)


@login_required
def generate_recommendations(request):
    """Generate new AI recommendations for a farm"""
    
    if request.method == 'POST':
        farm_id = request.POST.get('farm_id')
        farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
        
        try:
            # Run AI recommendation engine
            result = run_ai_recommendations_for_farm(farm, request.user)
            
            messages.success(
                request, 
                f"Generated {result['total_recommendations']} new recommendations for {farm.name}. "
                f"{result['urgent_count']} urgent recommendations require immediate attention."
            )
            
            # Add detailed breakdown message
            if result['recommendations_by_type']:
                breakdown = []
                for rec_type, count in result['recommendations_by_type'].items():
                    if count > 0:
                        breakdown.append(f"{count} {rec_type.replace('_', ' ')}")
                
                if breakdown:
                    messages.info(request, f"Breakdown: {', '.join(breakdown)}")
            
        except Exception as e:
            messages.error(request, f"Error generating recommendations: {str(e)}")
    
    return redirect('recommendations:dashboard')


@login_required
def recommendation_detail(request, recommendation_id):
    """Detailed view of a specific recommendation"""
    
    recommendation = get_object_or_404(
        RecommendationEngine, 
        id=recommendation_id, 
        user=request.user
    )
    
    # Get related data based on recommendation type
    related_data = None
    
    if recommendation.recommendation_type == 'crop_selection':
        crop_rec_id = recommendation.metadata.get('crop_recommendation_id')
        if crop_rec_id:
            related_data = get_object_or_404(CropRecommendation, id=crop_rec_id)
    
    elif recommendation.recommendation_type == 'weather_based':
        weather_rec_id = recommendation.metadata.get('weather_recommendation_id')
        if weather_rec_id:
            related_data = get_object_or_404(WeatherRecommendation, id=weather_rec_id)
    
    elif recommendation.recommendation_type == 'pest_disease':
        pest_alert_id = recommendation.metadata.get('pest_alert_id')
        if pest_alert_id:
            related_data = get_object_or_404(PestDiseaseAlert, id=pest_alert_id)
    
    elif recommendation.recommendation_type == 'resource_optimization':
        resource_opt_id = recommendation.metadata.get('resource_optimization_id')
        if resource_opt_id:
            related_data = get_object_or_404(ResourceOptimization, id=resource_opt_id)
    
    elif recommendation.recommendation_type == 'market_timing':
        price_pred_id = recommendation.metadata.get('price_prediction_id')
        if price_pred_id:
            related_data = get_object_or_404(MarketPricePrediction, id=price_pred_id)
    
    # Get or create feedback
    feedback = None
    try:
        feedback = RecommendationFeedback.objects.get(
            recommendation=recommendation,
            user=request.user
        )
    except RecommendationFeedback.DoesNotExist:
        pass
    
    # Handle feedback submission
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'implement':
            recommendation.is_implemented = True
            recommendation.implemented_at = timezone.now()
            recommendation.save()
            messages.success(request, "Recommendation marked as implemented.")
        
        elif action == 'dismiss':
            recommendation.is_active = False
            recommendation.save()
            messages.info(request, "Recommendation dismissed.")
        
        elif action == 'feedback':
            usefulness_rating = request.POST.get('usefulness_rating')
            accuracy_rating = request.POST.get('accuracy_rating')
            implementation_difficulty = request.POST.get('implementation_difficulty')
            was_implemented = request.POST.get('was_implemented') == 'on'
            comments = request.POST.get('comments', '')
            
            if feedback:
                # Update existing feedback
                feedback.usefulness_rating = usefulness_rating
                feedback.accuracy_rating = accuracy_rating
                feedback.implementation_difficulty = implementation_difficulty
                feedback.was_implemented = was_implemented
                feedback.comments = comments
                feedback.save()
            else:
                # Create new feedback
                feedback = RecommendationFeedback.objects.create(
                    recommendation=recommendation,
                    user=request.user,
                    usefulness_rating=usefulness_rating,
                    accuracy_rating=accuracy_rating,
                    implementation_difficulty=implementation_difficulty,
                    was_implemented=was_implemented,
                    comments=comments
                )
            
            # Update recommendation rating
            recommendation.feedback_rating = usefulness_rating
            recommendation.feedback_notes = comments
            recommendation.save()
            
            messages.success(request, "Thank you for your feedback!")
        
        return redirect('recommendations:detail', recommendation_id=recommendation.id)
    
    context = {
        'recommendation': recommendation,
        'related_data': related_data,
        'feedback': feedback,
        'page_title': f'Recommendation: {recommendation.title}'
    }
    
    return render(request, 'recommendations/detail.html', context)


@login_required
def recommendations_list(request):
    """List all recommendations with filtering"""
    
    # Get user's farms
    user_farms = Farm.objects.filter(owner=request.user)
    
    # Get filter parameters
    farm_id = request.GET.get('farm_id')
    recommendation_type = request.GET.get('type')
    priority = request.GET.get('priority')
    status = request.GET.get('status', 'active')  # active, implemented, dismissed
    
    # Build query
    recommendations = RecommendationEngine.objects.filter(user=request.user)
    
    if farm_id:
        recommendations = recommendations.filter(farm_id=farm_id)
    
    if recommendation_type:
        recommendations = recommendations.filter(recommendation_type=recommendation_type)
    
    if priority:
        recommendations = recommendations.filter(priority=priority)
    
    if status == 'active':
        recommendations = recommendations.filter(is_active=True, is_implemented=False)
    elif status == 'implemented':
        recommendations = recommendations.filter(is_implemented=True)
    elif status == 'dismissed':
        recommendations = recommendations.filter(is_active=False)
    
    recommendations = recommendations.order_by('-priority', '-created_at')
    
    # Pagination
    paginator = Paginator(recommendations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter choices
    recommendation_types = RecommendationEngine.RECOMMENDATION_TYPES
    priority_levels = RecommendationEngine.PRIORITY_LEVELS
    
    context = {
        'page_obj': page_obj,
        'user_farms': user_farms,
        'recommendation_types': recommendation_types,
        'priority_levels': priority_levels,
        'current_filters': {
            'farm_id': farm_id,
            'type': recommendation_type,
            'priority': priority,
            'status': status
        },
        'page_title': 'All Recommendations'
    }
    
    return render(request, 'recommendations/list.html', context)


@login_required
def pest_disease_alerts(request):
    """View pest and disease alerts"""
    
    # Get user's farms
    user_farms = Farm.objects.filter(owner=request.user)
    
    # Get filter parameters
    farm_id = request.GET.get('farm_id')
    severity = request.GET.get('severity')
    alert_type = request.GET.get('type')
    
    # Build query
    alerts = PestDiseaseAlert.objects.filter(farm__owner=request.user)
    
    if farm_id:
        alerts = alerts.filter(farm_id=farm_id)
    
    if severity:
        alerts = alerts.filter(severity_level=severity)
    
    if alert_type:
        alerts = alerts.filter(type=alert_type)
    
    alerts = alerts.order_by('-alert_date')
    
    # Pagination
    paginator = Paginator(alerts, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    stats = {
        'total_active': alerts.filter(is_active=True).count(),
        'critical_alerts': alerts.filter(severity_level='critical', is_active=True).count(),
        'recent_alerts': alerts.filter(
            alert_date__gte=timezone.now() - timedelta(days=7)
        ).count()
    }
    
    context = {
        'page_obj': page_obj,
        'user_farms': user_farms,
        'severity_levels': PestDiseaseAlert.SEVERITY_LEVELS,
        'alert_types': [('pest', 'Pest'), ('disease', 'Disease'), ('weed', 'Weed')],
        'stats': stats,
        'current_filters': {
            'farm_id': farm_id,
            'severity': severity,
            'type': alert_type
        },
        'page_title': 'Pest & Disease Alerts'
    }
    
    return render(request, 'recommendations/pest_alerts.html', context)


@login_required
def market_predictions(request):
    """View market price predictions"""
    
    # Get user's farms
    user_farms = Farm.objects.filter(owner=request.user)
    
    # Get filter parameters
    crop_id = request.GET.get('crop_id')
    
    # Build query
    predictions = MarketPricePrediction.objects.all()
    
    if crop_id:
        predictions = predictions.filter(crop_id=crop_id)
    
    predictions = predictions.order_by('-prediction_date')
    
    # Pagination
    paginator = Paginator(predictions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available crops for filter
    from apps.farms.models import Crop
    available_crops = Crop.objects.all()
    
    context = {
        'page_obj': page_obj,
        'available_crops': available_crops,
        'current_filters': {
            'crop_id': crop_id
        },
        'page_title': 'Market Price Predictions'
    }
    
    return render(request, 'recommendations/market_predictions.html', context)


@login_required
def resource_optimizations(request):
    """View resource optimization recommendations"""
    
    # Get user's farms
    user_farms = Farm.objects.filter(owner=request.user)
    
    # Get filter parameters
    farm_id = request.GET.get('farm_id')
    resource_type = request.GET.get('resource_type')
    
    # Build query
    optimizations = ResourceOptimization.objects.filter(farm__owner=request.user)
    
    if farm_id:
        optimizations = optimizations.filter(farm_id=farm_id)
    
    if resource_type:
        optimizations = optimizations.filter(resource_type=resource_type)
    
    optimizations = optimizations.order_by('-potential_savings')
    
    # Pagination
    paginator = Paginator(optimizations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate total potential savings
    total_savings = sum(opt.potential_savings for opt in optimizations)
    
    context = {
        'page_obj': page_obj,
        'user_farms': user_farms,
        'resource_types': ResourceOptimization.RESOURCE_TYPES,
        'total_savings': total_savings,
        'current_filters': {
            'farm_id': farm_id,
            'resource_type': resource_type
        },
        'page_title': 'Resource Optimizations'
    }
    
    return render(request, 'recommendations/resource_optimizations.html', context)


@login_required
def ajax_recommendation_action(request):
    """AJAX endpoint for recommendation actions"""
    
    if request.method == 'POST':
        recommendation_id = request.POST.get('recommendation_id')
        action = request.POST.get('action')
        
        try:
            recommendation = RecommendationEngine.objects.get(
                id=recommendation_id,
                user=request.user
            )
            
            if action == 'implement':
                recommendation.is_implemented = True
                recommendation.implemented_at = timezone.now()
                recommendation.save()
                return JsonResponse({'status': 'success', 'message': 'Recommendation implemented'})
            
            elif action == 'dismiss':
                recommendation.is_active = False
                recommendation.save()
                return JsonResponse({'status': 'success', 'message': 'Recommendation dismissed'})
            
            elif action == 'reactivate':
                recommendation.is_active = True
                recommendation.save()
                return JsonResponse({'status': 'success', 'message': 'Recommendation reactivated'})
            
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid action'})
                
        except RecommendationEngine.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Recommendation not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
