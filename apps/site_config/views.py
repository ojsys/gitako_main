from django.shortcuts import render
from .models import (
    SiteSettings, HeroSlider, Feature, Testimonial, Statistic,
    FeaturePage, FeatureDetail, PricingPage, PricingPlan, PricingFAQ,
    AboutPage, StorySection, TeamMember, CompanyValue,
    ContactPage, ContactFAQ
)

def home(request):
    """View for the home page"""
    site_settings = SiteSettings.load()
    hero_sliders = HeroSlider.objects.filter(is_active=True)
    features = Feature.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)
    statistics = Statistic.objects.filter(is_active=True)
    
    context = {
        'site_settings': site_settings,
        'hero_sliders': hero_sliders,
        'features': features,
        'testimonials': testimonials,
        'statistics': statistics,
    }
    
    return render(request, 'home.html', context)

def features(request):
    """View for the features page"""
    site_settings = SiteSettings.load()
    feature_page = FeaturePage.load()
    feature_details = FeatureDetail.objects.filter(is_active=True)
    
    context = {
        'site_settings': site_settings,
        'feature_page': feature_page,
        'feature_details': feature_details,
    }
    
    return render(request, 'features.html', context)

def pricing(request):
    """View for the pricing page"""
    site_settings = SiteSettings.load()
    pricing_page = PricingPage.load()
    pricing_plans = PricingPlan.objects.filter(is_active=True)
    pricing_faqs = PricingFAQ.objects.filter(is_active=True)
    
    context = {
        'site_settings': site_settings,
        'pricing_page': pricing_page,
        'pricing_plans': pricing_plans,
        'pricing_faqs': pricing_faqs,
    }
    
    return render(request, 'pricing.html', context)

def about(request):
    """View for the about page"""
    site_settings = SiteSettings.load()
    about_page = AboutPage.load()
    story_sections = StorySection.objects.filter(is_active=True)
    team_members = TeamMember.objects.filter(is_active=True)
    company_values = CompanyValue.objects.filter(is_active=True)
    
    context = {
        'site_settings': site_settings,
        'about_page': about_page,
        'story_sections': story_sections,
        'team_members': team_members,
        'company_values': company_values,
    }
    
    return render(request, 'about.html', context)

def contact(request):
    """View for the contact page"""
    site_settings = SiteSettings.load()
    contact_page = ContactPage.load()
    contact_faqs = ContactFAQ.objects.filter(is_active=True)
    
    context = {
        'site_settings': site_settings,
        'contact_page': contact_page,
        'contact_faqs': contact_faqs,
    }
    
    return render(request, 'contact.html', context)