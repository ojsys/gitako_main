from django.db import models
from django.core.cache import cache

class SingletonModel(models.Model):
    """Abstract base model for Singleton pattern models."""
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear the cache after saving
        cache.clear()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """Site-wide settings for the Gitako application."""
    site_name = models.CharField(max_length=100, default="Gitako")
    site_description = models.TextField(blank=True, null=True)
    
    # Logo and Favicon
    logo = models.ImageField(upload_to='site/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/favicon/', blank=True, null=True)
    
    # Hero Section
    hero_title = models.CharField(max_length=200, default="Smart Farm Management")
    hero_subtitle = models.TextField(default="Gitako helps you manage your farm operations efficiently, track activities, monitor inventory, and maximize profits with data-driven insights.")
    
    # Contact Information
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Social Media Links
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Footer Text
    footer_text = models.CharField(max_length=200, default="© Gitako. All rights reserved.")
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True)
    
    # SEO
    meta_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return "Site Settings"
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"


class HeroSlider(models.Model):
    """Hero slider images for the homepage."""
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='site/hero_slider/')
    button_text = models.CharField(max_length=50, blank=True, null=True)
    button_url = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Hero Slider"
        verbose_name_plural = "Hero Sliders"


class Feature(models.Model):
    """Features displayed on the homepage."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Material icon name (e.g., 'landscape')")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Feature"
        verbose_name_plural = "Features"


class Testimonial(models.Model):
    """Customer testimonials displayed on the homepage."""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='site/testimonials/')
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"


class Statistic(models.Model):
    """Statistics displayed on the homepage."""
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.label}: {self.value}"
    
    class Meta:
        ordering = ['order']
        verbose_name = "Statistic"
        verbose_name_plural = "Statistics"


# New models for the pages we created

class FeaturePage(SingletonModel):
    """Content for the Features page."""
    hero_title = models.CharField(max_length=200, default="Powerful Features for Modern Farming")
    hero_subtitle = models.TextField(default="Gitako provides a comprehensive suite of tools designed specifically for farmers to manage their operations efficiently and increase productivity.")
    hero_image = models.ImageField(upload_to='site/features/', blank=True, null=True)
    cta_text = models.CharField(max_length=100, default="Ready to Transform Your Farm?")
    cta_subtitle = models.TextField(default="Join thousands of farmers who are already using Gitako to improve their productivity and profitability.")
    
    def __str__(self):
        return "Features Page"
    
    class Meta:
        verbose_name = "Features Page"
        verbose_name_plural = "Features Page"


class FeatureDetail(models.Model):
    """Detailed features displayed on the Features page."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='site/feature_details/')
    bullet_points = models.TextField(help_text="Enter bullet points separated by new lines")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Feature Detail"
        verbose_name_plural = "Feature Details"


class PricingPage(SingletonModel):
    """Content for the Pricing page."""
    hero_title = models.CharField(max_length=200, default="Simple, Transparent Pricing")
    hero_subtitle = models.TextField(default="Choose the plan that fits your farm's needs. All plans include core features with different limits and capabilities.")
    faq_title = models.CharField(max_length=100, default="Frequently Asked Questions")
    cta_text = models.CharField(max_length=100, default="Still Have Questions?")
    cta_subtitle = models.TextField(default="Our team is ready to help you choose the right plan for your farm.")
    
    def __str__(self):
        return "Pricing Page"
    
    class Meta:
        verbose_name = "Pricing Page"
        verbose_name_plural = "Pricing Page"


class PricingPlan(models.Model):
    """Pricing plans displayed on the Pricing page."""
    name = models.CharField(max_length=50)
    subtitle = models.CharField(max_length=100)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField(help_text="Enter features separated by new lines. Prefix with '-' for inactive features.")
    is_popular = models.BooleanField(default=False)
    button_text = models.CharField(max_length=50, default="Get Started")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']
        verbose_name = "Pricing Plan"
        verbose_name_plural = "Pricing Plans"


class PricingFAQ(models.Model):
    """FAQs displayed on the Pricing page."""
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question
    
    class Meta:
        ordering = ['order']
        verbose_name = "Pricing FAQ"
        verbose_name_plural = "Pricing FAQs"


class AboutPage(SingletonModel):
    """Content for the About page."""
    hero_title = models.CharField(max_length=200, default="Our Mission")
    hero_subtitle = models.TextField(default="At Gitako, we're on a mission to empower farmers with technology that makes agriculture more productive, profitable, and sustainable.")
    hero_description = models.TextField(blank=True, null=True)
    hero_image = models.ImageField(upload_to='site/about/', blank=True, null=True)
    story_title = models.CharField(max_length=100, default="Our Story")
    story_subtitle = models.TextField(default="Gitako was born from a simple observation: farmers need better tools to manage their operations in the digital age.")
    team_title = models.CharField(max_length=100, default="Meet Our Team")
    values_title = models.CharField(max_length=100, default="Our Values")
    cta_text = models.CharField(max_length=100, default="Join the Gitako Community")
    cta_subtitle = models.TextField(default="Be part of our mission to transform agriculture through technology.")
    
    def __str__(self):
        return "About Page"
    
    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"


class StorySection(models.Model):
    """Story sections displayed on the About page."""
    title = models.CharField(max_length=100)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Story Section"
        verbose_name_plural = "Story Sections"


class TeamMember(models.Model):
    """Team members displayed on the About page."""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='site/team/')
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"


class CompanyValue(models.Model):
    """Company values displayed on the About page."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Material icon name (e.g., 'agriculture')")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        verbose_name = "Company Value"
        verbose_name_plural = "Company Values"


class ContactPage(SingletonModel):
    """Content for the Contact page."""
    hero_title = models.CharField(max_length=200, default="Get in Touch")
    hero_subtitle = models.TextField(default="Have questions about Gitako? We're here to help. Reach out to our team using any of the methods below.")
    office_address = models.TextField(default="123 Farm Street\nNairobi, Kenya\n00100")
    phone_number = models.CharField(max_length=20, default="+254 700 123 456")
    office_hours = models.CharField(max_length=100, default="Monday - Friday\n9:00 AM - 5:00 PM EAT")
    email_general = models.EmailField(default="info@gitako.com")
    email_support = models.EmailField(default="support@gitako.com")
    form_title = models.CharField(max_length=100, default="Send Us a Message")
    map_embed_url = models.URLField(max_length=400, default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3988.8177928497174!2d36.8170119!3d-1.2830983!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x182f10a22f8b05c5%3A0xece6bb3dea6c8c8c!2sNairobi%2C%20Kenya!5e0!3m2!1sen!2sus!4v1625123456789!5m2!1sen!2sus")
    faq_title = models.CharField(max_length=100, default="Frequently Asked Questions")
    cta_text = models.CharField(max_length=100, default="Ready to Get Started?")
    cta_subtitle = models.TextField(default="Join thousands of farmers who are already using Gitako to improve their productivity and profitability.")
    
    def __str__(self):
        return "Contact Page"
    
    class Meta:
        verbose_name = "Contact Page"
        verbose_name_plural = "Contact Page"


class ContactFAQ(models.Model):
    """FAQs displayed on the Contact page."""
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question
    
    class Meta:
        ordering = ['order']
        verbose_name = "Contact FAQ"
        verbose_name_plural = "Contact FAQs"