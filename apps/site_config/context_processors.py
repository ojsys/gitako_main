from .models import SiteSettings

def site_settings(request):
    """
    Context processor to add site settings to all templates
    """
    try:
        # Get the first site settings object or create one if it doesn't exist
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create(
                site_name="Gitako Farm Management",
                site_description="Empowering farmers with technology for sustainable agriculture and improved productivity."
            )
    except:
        # If there's an error (e.g., table doesn't exist yet during migrations)
        settings = None
    
    return {'site_settings': settings}