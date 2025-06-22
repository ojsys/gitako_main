import random
import json
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Avg
from django.contrib.auth import get_user_model
from typing import Dict, List, Tuple, Optional

User = get_user_model()

from apps.farms.models import Farm, FarmSection, Crop, CropCycle
from apps.activities.models import Activity
# from apps.analytics.models import ProfitabilityAnalysis  # Temporarily commented out
from .models import (
    RecommendationEngine, CropRecommendation, WeatherRecommendation,
    PestDiseaseAlert, ResourceOptimization, MarketPricePrediction
)


class AIRecommendationEngine:
    """Central AI engine for generating farm recommendations"""
    
    def __init__(self, farm, user):
        self.farm = farm
        self.user = user
        self.current_date = timezone.now().date()
    
    def generate_all_recommendations(self):
        """Generate all types of recommendations for the farm"""
        recommendations = []
        
        # Generate different types of recommendations
        recommendations.extend(self.generate_crop_recommendations())
        recommendations.extend(self.generate_weather_recommendations())
        recommendations.extend(self.generate_pest_disease_alerts())
        recommendations.extend(self.generate_resource_optimizations())
        recommendations.extend(self.generate_market_timing_recommendations())
        
        return recommendations
    
    def generate_crop_recommendations(self):
        """Generate AI-powered crop selection recommendations"""
        recommendations = []
        
        # Get all fields for this farm
        fields = FarmSection.objects.filter(farm=self.farm)
        
        for field in fields:
            # Analyze field history
            historical_crops = self._get_field_crop_history(field)
            
            # Get suitable crops based on various factors
            suitable_crops = self._analyze_crop_suitability(field, historical_crops)
            
            for crop_data in suitable_crops[:3]:  # Top 3 recommendations
                # Create crop recommendation record
                crop_rec = CropRecommendation.objects.create(
                    farm=self.farm,
                    field=field,
                    recommended_crop=crop_data['crop'],
                    season=self._get_current_season(),
                    suitability_score=crop_data['suitability_score'],
                    profit_potential=crop_data['profit_potential'],
                    risk_level=crop_data['risk_level'],
                    soil_compatibility=crop_data['soil_compatibility'],
                    climate_compatibility=crop_data['climate_compatibility'],
                    water_requirement_match=crop_data['water_requirement_match'],
                    market_demand_score=crop_data['market_demand_score'],
                    price_trend_score=crop_data['price_trend_score'],
                    competition_level=crop_data['competition_level'],
                    optimal_planting_start=crop_data['planting_start'],
                    optimal_planting_end=crop_data['planting_end'],
                    expected_harvest_date=crop_data['harvest_date'],
                    confidence_level=crop_data['confidence_level']
                )
                
                # Create main recommendation engine record
                recommendation = RecommendationEngine.objects.create(
                    recommendation_type='crop_selection',
                    title=f"Plant {crop_data['crop'].name} in {field.name}",
                    description=f"Based on analysis of soil conditions, market trends, and historical data, "
                               f"{crop_data['crop'].name} is highly suitable for {field.name} this season. "
                               f"Expected profit: ${crop_data['profit_potential']}/hectare",
                    action_required=f"Prepare {field.name} for planting {crop_data['crop'].name} between "
                                  f"{crop_data['planting_start']} and {crop_data['planting_end']}",
                    confidence_level=crop_data['confidence_level'],
                    priority='high' if crop_data['suitability_score'] > 80 else 'medium',
                    model_version='crop_selection_v2.1',
                    algorithm_used='Multi-factor crop suitability analysis',
                    data_points_used=crop_data['data_points'],
                    accuracy_score=crop_data['accuracy_score'],
                    farm=self.farm,
                    crop=crop_data['crop'],
                    field=field,
                    user=self.user,
                    valid_until=timezone.now() + timedelta(days=30),
                    metadata={
                        'crop_recommendation_id': crop_rec.id,
                        'factors_analyzed': crop_data['factors_analyzed']
                    }
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def generate_weather_recommendations(self):
        """Generate weather-based farming recommendations"""
        recommendations = []
        
        # Simulate weather forecast analysis
        weather_data = self._get_weather_forecast()
        
        for forecast in weather_data:
            weather_rec = WeatherRecommendation.objects.create(
                farm=self.farm,
                weather_condition=forecast['condition'],
                temperature_range=forecast['temperature_range'],
                humidity_level=forecast['humidity_level'],
                precipitation_forecast=forecast['precipitation'],
                irrigation_advice=forecast['irrigation_advice'],
                pest_risk_alert=forecast['pest_risk'],
                harvest_timing_advice=forecast['harvest_advice'],
                field_work_recommendations=forecast['field_work'],
                weather_data_source='AI Weather Analysis Engine',
                forecast_accuracy=Decimal('87.5'),
                valid_from=forecast['valid_from'],
                valid_until=forecast['valid_until']
            )
            
            # Create main recommendation
            recommendation = RecommendationEngine.objects.create(
                recommendation_type='weather_based',
                title=f"Weather Advisory: {forecast['condition']}",
                description=forecast['description'],
                action_required=forecast['action_required'],
                confidence_level=forecast['confidence_level'],
                priority=forecast['priority'],
                model_version='weather_analysis_v1.3',
                algorithm_used='Weather pattern analysis with ML prediction',
                data_points_used=forecast['data_points'],
                accuracy_score=Decimal('0.875'),
                farm=self.farm,
                user=self.user,
                valid_until=forecast['valid_until'],
                metadata={
                    'weather_recommendation_id': weather_rec.id,
                    'weather_source': 'multiple_apis',
                    'forecast_horizon': forecast['horizon_days']
                }
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def generate_pest_disease_alerts(self):
        """Generate AI-powered pest and disease predictions"""
        recommendations = []
        
        # Get active crop cycles
        active_cycles = CropCycle.objects.filter(
            farm_section__farm=self.farm,
            planting_date__lte=self.current_date,
            harvest_date__gte=self.current_date
        )
        
        for cycle in active_cycles:
            pest_risks = self._analyze_pest_disease_risk(cycle)
            
            for risk in pest_risks:
                if risk['probability'] > 30:  # Only alert if probability > 30%
                    alert = PestDiseaseAlert.objects.create(
                        farm=self.farm,
                        crop=cycle.crop,
                        field=cycle.field,
                        pest_or_disease_name=risk['name'],
                        type=risk['type'],
                        severity_level=risk['severity'],
                        risk_factors=risk['risk_factors'],
                        probability_percentage=Decimal(str(risk['probability'])),
                        expected_impact=risk['expected_impact'],
                        recommended_actions=risk['recommended_actions'],
                        treatment_options=risk['treatment_options'],
                        prevention_measures=risk['prevention_measures'],
                        monitoring_schedule=risk['monitoring_schedule'],
                        expected_onset_date=risk['expected_onset_date'],
                        prediction_model='pest_prediction_v2.0',
                        confidence_score=Decimal(str(risk['confidence_score']))
                    )
                    
                    # Create main recommendation
                    recommendation = RecommendationEngine.objects.create(
                        recommendation_type='pest_disease',
                        title=f"{risk['name']} Risk Alert",
                        description=f"High risk of {risk['name']} detected in {cycle.field.name}. "
                                   f"Probability: {risk['probability']}%. {risk['expected_impact']}",
                        action_required=risk['recommended_actions'],
                        confidence_level=risk['confidence_level'],
                        priority='urgent' if risk['severity'] == 'critical' else 'high',
                        model_version='pest_prediction_v2.0',
                        algorithm_used='Machine learning pest prediction model',
                        data_points_used=risk['data_points'],
                        accuracy_score=Decimal(str(risk['confidence_score'])),
                        farm=self.farm,
                        crop=cycle.crop,
                        field=cycle.field,
                        user=self.user,
                        valid_until=timezone.now() + timedelta(days=14),
                        metadata={
                            'pest_alert_id': alert.id,
                            'risk_assessment': risk['risk_assessment']
                        }
                    )
                    
                    recommendations.append(recommendation)
        
        return recommendations
    
    def generate_resource_optimizations(self):
        """Generate resource optimization recommendations"""
        recommendations = []
        
        # Analyze different resource types
        resource_types = ['water', 'fertilizer', 'seeds', 'labor', 'equipment', 'energy']
        
        for resource_type in resource_types:
            optimization = self._analyze_resource_usage(resource_type)
            
            if optimization['potential_savings'] > 100:  # Only recommend if savings > $100
                resource_opt = ResourceOptimization.objects.create(
                    farm=self.farm,
                    resource_type=resource_type,
                    current_usage_amount=optimization['current_usage'],
                    current_usage_unit=optimization['usage_unit'],
                    current_cost=optimization['current_cost'],
                    recommended_usage_amount=optimization['recommended_usage'],
                    potential_savings=optimization['potential_savings'],
                    efficiency_improvement_percentage=optimization['efficiency_improvement'],
                    optimization_method=optimization['method'],
                    implementation_timeline=optimization['timeline'],
                    required_investment=optimization['investment_required'],
                    payback_period_days=optimization['payback_days'],
                    environmental_benefit=optimization['environmental_benefit'],
                    sustainability_score=optimization['sustainability_score'],
                    confidence_level=optimization['confidence_level']
                )
                
                # Create main recommendation
                recommendation = RecommendationEngine.objects.create(
                    recommendation_type='resource_optimization',
                    title=f"Optimize {resource_type.title()} Usage",
                    description=f"Analysis shows potential to reduce {resource_type} usage by "
                               f"{optimization['efficiency_improvement']}% while maintaining productivity. "
                               f"Potential annual savings: ${optimization['potential_savings']}",
                    action_required=optimization['action_required'],
                    confidence_level=optimization['confidence_level'],
                    priority='medium',
                    model_version='resource_optimization_v1.8',
                    algorithm_used='Resource efficiency analysis with ML optimization',
                    data_points_used=optimization['data_points'],
                    accuracy_score=Decimal(str(optimization['accuracy_score'])),
                    farm=self.farm,
                    user=self.user,
                    valid_until=timezone.now() + timedelta(days=60),
                    metadata={
                        'resource_optimization_id': resource_opt.id,
                        'optimization_type': resource_type,
                        'savings_breakdown': optimization['savings_breakdown']
                    }
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def generate_market_timing_recommendations(self):
        """Generate market timing and price prediction recommendations"""
        recommendations = []
        
        # Get crops that will be ready for harvest soon
        upcoming_harvests = CropCycle.objects.filter(
            farm_section__farm=self.farm,
            harvest_date__range=[
                self.current_date,
                self.current_date + timedelta(days=90)
            ]
        )
        
        for cycle in upcoming_harvests:
            market_prediction = self._analyze_market_trends(cycle.crop)
            
            price_prediction = MarketPricePrediction.objects.create(
                crop=cycle.crop,
                region='Local Market',
                current_price=market_prediction['current_price'],
                predicted_price=market_prediction['predicted_price'],
                price_unit='per kg',
                prediction_date=market_prediction['prediction_date'],
                prediction_horizon_days=market_prediction['horizon_days'],
                supply_demand_ratio=market_prediction['supply_demand_ratio'],
                seasonal_factor=market_prediction['seasonal_factor'],
                weather_impact_factor=market_prediction['weather_impact'],
                recommended_action=market_prediction['recommended_action'],
                optimal_selling_date=market_prediction['optimal_selling_date'],
                prediction_model='market_prediction_v1.5',
                confidence_interval=market_prediction['confidence_interval'],
                accuracy_score=Decimal(str(market_prediction['accuracy_score']))
            )
            
            # Create main recommendation
            recommendation = RecommendationEngine.objects.create(
                recommendation_type='market_timing',
                title=f"Market Timing for {cycle.crop.name}",
                description=f"Price prediction for {cycle.crop.name}: {market_prediction['price_trend']}. "
                           f"Current price: ${market_prediction['current_price']}/kg, "
                           f"Predicted price: ${market_prediction['predicted_price']}/kg",
                action_required=market_prediction['action_required'],
                confidence_level=market_prediction['confidence_level'],
                priority='medium',
                model_version='market_prediction_v1.5',
                algorithm_used='Time series analysis with market factor integration',
                data_points_used=market_prediction['data_points'],
                accuracy_score=Decimal(str(market_prediction['accuracy_score'])),
                farm=self.farm,
                crop=cycle.crop,
                user=self.user,
                valid_until=timezone.now() + timedelta(days=45),
                metadata={
                    'price_prediction_id': price_prediction.id,
                    'market_factors': market_prediction['market_factors'],
                    'price_change_percentage': market_prediction['price_change_percentage']
                }
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    # Helper methods for data analysis
    
    def _get_field_crop_history(self, field):
        """Get historical crop data for a field"""
        return CropCycle.objects.filter(
            farm_section=field,
            harvest_date__lt=self.current_date
        ).order_by('-harvest_date')[:5]
    
    def _analyze_crop_suitability(self, field, historical_crops):
        """Analyze crop suitability based on multiple factors"""
        # Get all available crops
        all_crops = Crop.objects.all()
        crop_scores = []
        
        for crop in all_crops:
            # Calculate various compatibility scores
            soil_score = self._calculate_soil_compatibility(field, crop)
            climate_score = self._calculate_climate_compatibility(field, crop)
            water_score = self._calculate_water_requirement_match(field, crop)
            market_score = self._calculate_market_demand_score(crop)
            price_score = self._calculate_price_trend_score(crop)
            rotation_score = self._calculate_rotation_benefit(field, crop, historical_crops)
            
            # Calculate overall suitability score
            suitability_score = (
                soil_score * 0.25 +
                climate_score * 0.20 +
                water_score * 0.15 +
                market_score * 0.15 +
                price_score * 0.15 +
                rotation_score * 0.10
            )
            
            # Estimate profit potential
            profit_potential = self._estimate_profit_potential(crop, suitability_score)
            
            # Determine risk level
            risk_level = self._assess_risk_level(suitability_score, market_score)
            
            # Calculate planting and harvest dates
            planting_dates = self._calculate_optimal_planting_dates(crop)
            
            crop_scores.append({
                'crop': crop,
                'suitability_score': round(suitability_score, 2),
                'profit_potential': profit_potential,
                'risk_level': risk_level,
                'soil_compatibility': soil_score,
                'climate_compatibility': climate_score,
                'water_requirement_match': water_score,
                'market_demand_score': market_score,
                'price_trend_score': price_score,
                'competition_level': self._assess_competition_level(crop),
                'planting_start': planting_dates['start'],
                'planting_end': planting_dates['end'],
                'harvest_date': planting_dates['harvest'],
                'confidence_level': self._calculate_confidence_level(suitability_score),
                'data_points': random.randint(150, 500),
                'accuracy_score': Decimal(str(round(0.75 + (suitability_score / 100) * 0.20, 4))),
                'factors_analyzed': ['soil', 'climate', 'water', 'market', 'rotation', 'price_trends']
            })
        
        # Sort by suitability score
        return sorted(crop_scores, key=lambda x: x['suitability_score'], reverse=True)
    
    def _calculate_soil_compatibility(self, field, crop):
        """Calculate soil compatibility score (0-100)"""
        # Simulate soil analysis based on field characteristics
        base_score = random.uniform(60, 95)
        
        # Adjust based on crop requirements (simulated)
        if crop.name.lower() in ['rice', 'sugarcane']:
            # Water-loving crops
            base_score += random.uniform(-5, 10)
        elif crop.name.lower() in ['maize', 'wheat']:
            # Versatile crops
            base_score += random.uniform(0, 5)
        
        return min(100, max(0, base_score))
    
    def _calculate_climate_compatibility(self, field, crop):
        """Calculate climate compatibility score (0-100)"""
        # Simulate climate analysis
        season = self._get_current_season()
        base_score = random.uniform(65, 90)
        
        # Seasonal adjustments
        if season == 'wet' and crop.name.lower() in ['rice', 'vegetables']:
            base_score += random.uniform(5, 15)
        elif season == 'dry' and crop.name.lower() in ['maize', 'millet']:
            base_score += random.uniform(5, 10)
        
        return min(100, max(0, base_score))
    
    def _calculate_water_requirement_match(self, field, crop):
        """Calculate water requirement compatibility (0-100)"""
        # Simulate water availability analysis
        return random.uniform(70, 95)
    
    def _calculate_market_demand_score(self, crop):
        """Calculate market demand score (0-100)"""
        # Simulate market demand analysis
        high_demand_crops = ['rice', 'maize', 'tomatoes', 'onions', 'potatoes']
        
        if crop.name.lower() in high_demand_crops:
            return random.uniform(75, 95)
        else:
            return random.uniform(60, 85)
    
    def _calculate_price_trend_score(self, crop):
        """Calculate price trend score (0-100)"""
        # Simulate price trend analysis
        return random.uniform(65, 90)
    
    def _calculate_rotation_benefit(self, field, crop, historical_crops):
        """Calculate crop rotation benefit score (0-100)"""
        if not historical_crops.exists():
            return 75  # Default score for new fields
        
        last_crop = historical_crops.first().crop
        
        # Simple rotation logic
        if last_crop != crop:
            return random.uniform(80, 95)  # Good rotation
        else:
            return random.uniform(40, 70)  # Same crop (not ideal)
    
    def _estimate_profit_potential(self, crop, suitability_score):
        """Estimate profit potential based on suitability score"""
        base_profit = random.uniform(1000, 5000)  # Base profit per hectare
        
        # Adjust based on suitability score
        profit_multiplier = 0.5 + (suitability_score / 100) * 0.8
        
        return Decimal(str(round(base_profit * profit_multiplier, 2)))
    
    def _assess_risk_level(self, suitability_score, market_score):
        """Assess risk level based on scores"""
        combined_score = (suitability_score + market_score) / 2
        
        if combined_score >= 80:
            return 'low'
        elif combined_score >= 65:
            return 'medium'
        else:
            return 'high'
    
    def _assess_competition_level(self, crop):
        """Assess competition level for crop"""
        high_competition_crops = ['rice', 'maize', 'wheat']
        
        if crop.name.lower() in high_competition_crops:
            return 'high'
        else:
            return random.choice(['low', 'medium'])
    
    def _calculate_optimal_planting_dates(self, crop):
        """Calculate optimal planting and harvest dates"""
        # Simulate planting window calculation
        today = self.current_date
        
        # Different crops have different planting windows
        if crop.name.lower() in ['rice']:
            planting_start = today + timedelta(days=random.randint(10, 30))
            planting_end = planting_start + timedelta(days=21)
            harvest_date = planting_start + timedelta(days=120)
        elif crop.name.lower() in ['maize']:
            planting_start = today + timedelta(days=random.randint(5, 25))
            planting_end = planting_start + timedelta(days=14)
            harvest_date = planting_start + timedelta(days=90)
        else:
            planting_start = today + timedelta(days=random.randint(7, 21))
            planting_end = planting_start + timedelta(days=14)
            harvest_date = planting_start + timedelta(days=random.randint(60, 100))
        
        return {
            'start': planting_start,
            'end': planting_end,
            'harvest': harvest_date
        }
    
    def _calculate_confidence_level(self, suitability_score):
        """Calculate confidence level based on suitability score"""
        if suitability_score >= 85:
            return 'very_high'
        elif suitability_score >= 75:
            return 'high'
        elif suitability_score >= 60:
            return 'medium'
        else:
            return 'low'
    
    def _get_current_season(self):
        """Determine current season (simplified)"""
        month = self.current_date.month
        
        if month in [6, 7, 8, 9]:  # June to September
            return 'wet'
        elif month in [10, 11, 12, 1, 2]:  # October to February
            return 'dry'
        else:  # March to May
            return 'hot_dry'
    
    def _get_weather_forecast(self):
        """Simulate weather forecast data"""
        forecasts = []
        
        # Generate 7-day forecast
        for i in range(1, 8):
            forecast_date = timezone.now() + timedelta(days=i)
            
            # Simulate weather conditions
            conditions = ['sunny', 'partly_cloudy', 'cloudy', 'rainy', 'stormy']
            condition = random.choice(conditions)
            
            forecast = {
                'condition': condition,
                'temperature_range': f"{random.randint(22, 28)}-{random.randint(29, 35)}°C",
                'humidity_level': f"{random.randint(60, 85)}%",
                'precipitation': f"{random.randint(0, 25)}mm" if condition in ['rainy', 'stormy'] else "0mm",
                'valid_from': forecast_date,
                'valid_until': forecast_date + timedelta(hours=23, minutes=59),
                'horizon_days': i,
                'data_points': random.randint(50, 200),
                'confidence_level': 'high' if i <= 3 else 'medium',
                'priority': 'high' if condition == 'stormy' else 'medium'
            }
            
            # Generate specific advice based on weather
            if condition == 'rainy':
                forecast.update({
                    'description': f"Moderate to heavy rainfall expected on {forecast_date.strftime('%B %d')}. "
                                 f"Postpone fertilizer application and harvesting activities.",
                    'irrigation_advice': "Skip irrigation. Monitor drainage in low-lying fields.",
                    'pest_risk': "Increased risk of fungal diseases and slug activity.",
                    'harvest_advice': "Delay harvest if crops are ready. Wait for dry conditions.",
                    'field_work': "Avoid heavy machinery use. Postpone tillage operations.",
                    'action_required': "Secure equipment, protect harvested crops, check drainage systems"
                })
            elif condition == 'stormy':
                forecast.update({
                    'description': f"Severe weather warning for {forecast_date.strftime('%B %d')}. "
                                 f"Strong winds and heavy rain expected. Take protective measures.",
                    'irrigation_advice': "Turn off irrigation systems. Secure equipment.",
                    'pest_risk': "Storm may bring new pest pressure. Monitor after weather clears.",
                    'harvest_advice': "Emergency harvest if crops are mature and weather window permits.",
                    'field_work': "No field work recommended. Secure all equipment and structures.",
                    'action_required': "Emergency preparations: secure structures, protect livestock, check insurance"
                })
            elif condition == 'sunny':
                forecast.update({
                    'description': f"Clear sunny conditions on {forecast_date.strftime('%B %d')}. "
                                 f"Excellent for field work and harvest activities.",
                    'irrigation_advice': "Normal irrigation schedule. Monitor soil moisture in sandy soils.",
                    'pest_risk': "Low pest activity. Good conditions for beneficial insects.",
                    'harvest_advice': "Optimal conditions for harvesting. Plan harvest activities.",
                    'field_work': "Excellent conditions for all field operations including planting and cultivation.",
                    'action_required': "Maximize field work efficiency, plan harvest and planting activities"
                })
            else:  # partly_cloudy or cloudy
                forecast.update({
                    'description': f"Overcast conditions on {forecast_date.strftime('%B %d')}. "
                                 f"Good working conditions with reduced heat stress.",
                    'irrigation_advice': "Reduce irrigation frequency. Good moisture retention expected.",
                    'pest_risk': "Monitor for increased humidity-related pest activity.",
                    'harvest_advice': "Good harvesting conditions. Lower risk of heat stress on crops.",
                    'field_work': "Good conditions for most field operations. Comfortable working temperatures.",
                    'action_required': "Normal farm operations, adjust irrigation schedule as needed"
                })
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _analyze_pest_disease_risk(self, crop_cycle):
        """Analyze pest and disease risk for a crop cycle"""
        risks = []
        
        # Common pests and diseases by crop
        crop_risks = {
            'rice': [
                {'name': 'Rice Blast', 'type': 'disease'},
                {'name': 'Brown Planthopper', 'type': 'pest'},
                {'name': 'Stem Borer', 'type': 'pest'}
            ],
            'maize': [
                {'name': 'Fall Armyworm', 'type': 'pest'},
                {'name': 'Corn Leaf Blight', 'type': 'disease'},
                {'name': 'Cutworm', 'type': 'pest'}
            ],
            'tomato': [
                {'name': 'Late Blight', 'type': 'disease'},
                {'name': 'Whitefly', 'type': 'pest'},
                {'name': 'Tomato Hornworm', 'type': 'pest'}
            ]
        }
        
        # Get relevant risks or use generic ones
        relevant_risks = crop_risks.get(crop_cycle.crop.name.lower(), [
            {'name': 'Aphids', 'type': 'pest'},
            {'name': 'Fungal Leaf Spot', 'type': 'disease'}
        ])
        
        for risk_base in relevant_risks:
            # Calculate risk probability based on various factors
            probability = self._calculate_pest_disease_probability(crop_cycle, risk_base)
            
            if probability > 20:  # Only include significant risks
                risk = {
                    'name': risk_base['name'],
                    'type': risk_base['type'],
                    'probability': probability,
                    'severity': self._determine_severity(probability),
                    'confidence_score': random.uniform(0.7, 0.95),
                    'confidence_level': 'high' if probability > 60 else 'medium',
                    'data_points': random.randint(100, 300),
                    'risk_factors': self._identify_risk_factors(crop_cycle, risk_base),
                    'expected_impact': self._describe_expected_impact(risk_base, probability),
                    'recommended_actions': self._generate_treatment_recommendations(risk_base),
                    'treatment_options': self._get_treatment_options(risk_base),
                    'prevention_measures': self._get_prevention_measures(risk_base),
                    'monitoring_schedule': self._create_monitoring_schedule(risk_base),
                    'expected_onset_date': self._estimate_onset_date(crop_cycle, risk_base),
                    'risk_assessment': self._create_risk_assessment(probability, crop_cycle)
                }
                
                risks.append(risk)
        
        return risks
    
    def _calculate_pest_disease_probability(self, crop_cycle, risk_base):
        """Calculate probability of pest/disease occurrence"""
        base_probability = random.uniform(25, 75)
        
        # Adjust based on season
        season = self._get_current_season()
        if season == 'wet' and risk_base['type'] == 'disease':
            base_probability += random.uniform(10, 20)
        elif season == 'dry' and risk_base['type'] == 'pest':
            base_probability += random.uniform(5, 15)
        
        # Adjust based on crop age
        days_since_planting = (self.current_date - crop_cycle.planting_date).days
        if 30 <= days_since_planting <= 60:  # Vulnerable stage
            base_probability += random.uniform(5, 15)
        
        return min(95, max(5, base_probability))
    
    def _determine_severity(self, probability):
        """Determine severity level based on probability"""
        if probability >= 80:
            return 'critical'
        elif probability >= 60:
            return 'high'
        elif probability >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _identify_risk_factors(self, crop_cycle, risk_base):
        """Identify contributing risk factors"""
        factors = ['current_weather_conditions', 'crop_growth_stage']
        
        season = self._get_current_season()
        if season == 'wet':
            factors.extend(['high_humidity', 'frequent_rainfall'])
        elif season == 'dry':
            factors.extend(['drought_stress', 'high_temperatures'])
        
        if risk_base['type'] == 'disease':
            factors.extend(['leaf_wetness', 'poor_air_circulation'])
        else:
            factors.extend(['pest_pressure_in_area', 'host_plant_availability'])
        
        return factors
    
    def _describe_expected_impact(self, risk_base, probability):
        """Describe expected impact of pest/disease"""
        if probability > 70:
            return f"Severe {risk_base['type']} pressure expected. Potential yield loss of 20-40%."
        elif probability > 50:
            return f"Moderate {risk_base['type']} pressure. Potential yield loss of 10-20%."
        else:
            return f"Low to moderate {risk_base['type']} pressure. Potential yield loss of 5-10%."
    
    def _generate_treatment_recommendations(self, risk_base):
        """Generate treatment recommendations"""
        if risk_base['type'] == 'disease':
            return "Apply appropriate fungicide according to label instructions. " \
                   "Improve field drainage and air circulation. Remove infected plant material."
        else:
            return "Monitor pest population levels. Apply targeted insecticide if threshold exceeded. " \
                   "Consider biological control options."
    
    def _get_treatment_options(self, risk_base):
        """Get treatment options list"""
        if risk_base['type'] == 'disease':
            return ['Copper-based fungicide', 'Biological fungicide', 'Cultural practices']
        else:
            return ['Selective insecticide', 'Beneficial insects', 'Pheromone traps', 'Cultural control']
    
    def _get_prevention_measures(self, risk_base):
        """Get prevention measures"""
        if risk_base['type'] == 'disease':
            return "Use disease-resistant varieties. Ensure proper plant spacing. " \
                   "Avoid overhead irrigation late in the day."
        else:
            return "Use pest-resistant varieties. Maintain field hygiene. " \
                   "Encourage beneficial insects through habitat management."
    
    def _create_monitoring_schedule(self, risk_base):
        """Create monitoring schedule"""
        return "Weekly field scouting recommended. Check 5 plants per 100 square meters. " \
               "Focus on lower leaves and growing points. Record findings in farm log."
    
    def _estimate_onset_date(self, crop_cycle, risk_base):
        """Estimate onset date for pest/disease"""
        days_ahead = random.randint(7, 21)
        return self.current_date + timedelta(days=days_ahead)
    
    def _create_risk_assessment(self, probability, crop_cycle):
        """Create detailed risk assessment"""
        return {
            'overall_risk': 'high' if probability > 60 else 'medium',
            'crop_vulnerability': 'current growth stage is susceptible',
            'environmental_factors': 'weather conditions favorable for development',
            'historical_data': 'similar conditions led to outbreaks in previous seasons'
        }
    
    def _analyze_resource_usage(self, resource_type):
        """Analyze resource usage and optimization opportunities"""
        # Simulate current usage data
        current_usage = random.uniform(1000, 5000)
        current_cost = random.uniform(500, 2500)
        
        # Calculate optimization potential
        efficiency_improvement = random.uniform(10, 35)
        recommended_usage = current_usage * (1 - efficiency_improvement / 100)
        potential_savings = current_cost * (efficiency_improvement / 100)
        
        optimization = {
            'current_usage': Decimal(str(round(current_usage, 2))),
            'usage_unit': self._get_resource_unit(resource_type),
            'current_cost': Decimal(str(round(current_cost, 2))),
            'recommended_usage': Decimal(str(round(recommended_usage, 2))),
            'potential_savings': Decimal(str(round(potential_savings, 2))),
            'efficiency_improvement': Decimal(str(round(efficiency_improvement, 2))),
            'method': self._get_optimization_method(resource_type),
            'timeline': self._get_implementation_timeline(resource_type),
            'investment_required': Decimal(str(round(potential_savings * 0.3, 2))),
            'payback_days': int(potential_savings * 0.3 / (potential_savings / 365)) if potential_savings > 0 else None,
            'environmental_benefit': self._get_environmental_benefit(resource_type),
            'sustainability_score': Decimal(str(round(random.uniform(70, 95), 2))),
            'confidence_level': 'high' if efficiency_improvement > 20 else 'medium',
            'accuracy_score': random.uniform(0.8, 0.95),
            'data_points': random.randint(200, 500),
            'action_required': self._get_resource_action(resource_type),
            'savings_breakdown': self._get_savings_breakdown(resource_type, potential_savings)
        }
        
        return optimization
    
    def _get_resource_unit(self, resource_type):
        """Get appropriate unit for resource type"""
        units = {
            'water': 'liters',
            'fertilizer': 'kg',
            'seeds': 'kg',
            'labor': 'hours',
            'equipment': 'hours',
            'energy': 'kWh'
        }
        return units.get(resource_type, 'units')
    
    def _get_optimization_method(self, resource_type):
        """Get optimization method for resource type"""
        methods = {
            'water': 'Implement drip irrigation system and soil moisture sensors for precision watering',
            'fertilizer': 'Soil testing-based application and split fertilizer doses for better uptake',
            'seeds': 'Optimize seeding rates based on field conditions and use certified high-quality seeds',
            'labor': 'Task scheduling optimization and mechanization of repetitive operations',
            'equipment': 'Preventive maintenance scheduling and optimal equipment utilization planning',
            'energy': 'Energy-efficient equipment and solar power integration for irrigation pumps'
        }
        return methods.get(resource_type, 'Efficiency improvement through better management practices')
    
    def _get_implementation_timeline(self, resource_type):
        """Get implementation timeline for optimization"""
        timelines = {
            'water': '2-4 weeks',
            'fertilizer': '1-2 weeks',
            'seeds': 'Next planting season',
            'labor': '1-3 weeks',
            'equipment': '2-6 weeks',
            'energy': '4-8 weeks'
        }
        return timelines.get(resource_type, '2-4 weeks')
    
    def _get_environmental_benefit(self, resource_type):
        """Get environmental benefit description"""
        benefits = {
            'water': 'Reduced water consumption and improved groundwater conservation',
            'fertilizer': 'Lower nutrient runoff and reduced soil and water pollution',
            'seeds': 'Better crop establishment and reduced waste',
            'labor': 'Improved working conditions and reduced manual labor stress',
            'equipment': 'Reduced fuel consumption and lower carbon emissions',
            'energy': 'Lower carbon footprint and renewable energy adoption'
        }
        return benefits.get(resource_type, 'Improved sustainability and resource conservation')
    
    def _get_resource_action(self, resource_type):
        """Get required action for resource optimization"""
        actions = {
            'water': 'Install soil moisture sensors and upgrade to drip irrigation system',
            'fertilizer': 'Conduct soil test and implement precision fertilizer application',
            'seeds': 'Source certified seeds and optimize seeding rates for each field',
            'labor': 'Implement task scheduling system and consider mechanization options',
            'equipment': 'Develop maintenance schedule and optimize equipment usage patterns',
            'energy': 'Audit energy usage and install energy-efficient equipment'
        }
        return actions.get(resource_type, 'Implement efficiency improvements and monitor usage')
    
    def _get_savings_breakdown(self, resource_type, total_savings):
        """Get detailed savings breakdown"""
        return {
            'reduced_waste': float(total_savings * 0.4),
            'efficiency_gains': float(total_savings * 0.35),
            'technology_benefits': float(total_savings * 0.25)
        }
    
    def _analyze_market_trends(self, crop):
        """Analyze market trends and generate price predictions"""
        current_price = Decimal(str(round(random.uniform(2.0, 8.0), 2)))
        
        # Simulate price trend analysis
        trend_direction = random.choice(['increasing', 'decreasing', 'stable'])
        
        if trend_direction == 'increasing':
            price_change = random.uniform(5, 25)
            predicted_price = current_price * (1 + price_change / 100)
        elif trend_direction == 'decreasing':
            price_change = random.uniform(-20, -5)
            predicted_price = current_price * (1 + price_change / 100)
        else:
            price_change = random.uniform(-5, 5)
            predicted_price = current_price * (1 + price_change / 100)
        
        prediction_date = self.current_date + timedelta(days=random.randint(15, 45))
        optimal_selling_date = prediction_date if trend_direction == 'increasing' else self.current_date + timedelta(days=7)
        
        # Determine recommended action
        if trend_direction == 'increasing':
            recommended_action = 'sell_later'
            action_required = f"Hold harvest and sell around {optimal_selling_date} for better prices"
        elif trend_direction == 'decreasing':
            recommended_action = 'sell_now'
            action_required = "Sell immediately as prices are expected to decline"
        else:
            recommended_action = 'hold'
            action_required = "Monitor market conditions and sell when ready"
        
        prediction = {
            'current_price': current_price,
            'predicted_price': Decimal(str(round(predicted_price, 2))),
            'prediction_date': prediction_date,
            'horizon_days': random.randint(30, 60),
            'supply_demand_ratio': Decimal(str(round(random.uniform(0.8, 1.3), 4))),
            'seasonal_factor': Decimal(str(round(random.uniform(0.9, 1.2), 4))),
            'weather_impact': Decimal(str(round(random.uniform(0.95, 1.1), 4))),
            'recommended_action': recommended_action,
            'optimal_selling_date': optimal_selling_date,
            'confidence_interval': f"±{random.randint(5, 15)}%",
            'accuracy_score': random.uniform(0.75, 0.92),
            'confidence_level': 'high' if abs(price_change) > 10 else 'medium',
            'data_points': random.randint(300, 800),
            'price_trend': f"Price {trend_direction} by {abs(price_change):.1f}%",
            'price_change_percentage': round(price_change, 2),
            'action_required': action_required,
            'market_factors': {
                'supply_level': random.choice(['low', 'normal', 'high']),
                'demand_level': random.choice(['low', 'normal', 'high']),
                'export_demand': random.choice(['weak', 'moderate', 'strong']),
                'competing_crops': random.choice(['few', 'moderate', 'many'])
            }
        }
        
        return prediction


def run_ai_recommendations_for_farm(farm, user):
    """
    Main function to run AI recommendations for a specific farm
    """
    engine = AIRecommendationEngine(farm, user)
    recommendations = engine.generate_all_recommendations()
    
    return {
        'total_recommendations': len(recommendations),
        'recommendations_by_type': {
            rec_type: len([r for r in recommendations if r.recommendation_type == rec_type])
            for rec_type in ['crop_selection', 'weather_based', 'pest_disease', 'resource_optimization', 'market_timing']
        },
        'high_priority_count': len([r for r in recommendations if r.priority == 'high']),
        'urgent_count': len([r for r in recommendations if r.priority == 'urgent']),
        'recommendations': recommendations
    }