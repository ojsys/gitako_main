from django.shortcuts import render

def home(request):
    """View for the home page"""
    return render(request, 'home.html')

def features(request):
    """View for the features page"""
    return render(request, 'features.html')

def pricing(request):
    """View for the pricing page"""
    return render(request, 'pricing.html')

def about(request):
    """View for the about page"""
    return render(request, 'about.html')

def contact(request):
    """View for the contact page"""
    return render(request, 'contact.html')