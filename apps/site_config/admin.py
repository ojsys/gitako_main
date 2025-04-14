from django.contrib import admin
from .models import (
    SiteSettings, HeroSlider, Feature, Testimonial, Statistic,
    FeaturePage, FeatureDetail, PricingPage, PricingPlan, PricingFAQ,
    AboutPage, StorySection, TeamMember, CompanyValue,
    ContactPage, ContactFAQ
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'site_description', 'logo', 'favicon')
        }),
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
        ('SEO & Analytics', {
            'fields': ('google_analytics_id', 'meta_keywords', 'meta_description')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('icon', 'order', 'is_active')
    search_fields = ('title', 'description')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'position', 'content')


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'order', 'is_active')
    list_editable = ('value', 'order', 'is_active')
    search_fields = ('label', 'value')


# Feature Page Admin
@admin.register(FeaturePage)
class FeaturePageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image')
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_subtitle')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FeatureDetail)
class FeatureDetailAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description', 'bullet_points')


# Pricing Page Admin
@admin.register(PricingPage)
class PricingPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('FAQ Section', {
            'fields': ('faq_title',)
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_subtitle')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_price', 'annual_price', 'is_popular', 'order', 'is_active')
    list_editable = ('is_popular', 'order', 'is_active')
    search_fields = ('name', 'subtitle', 'features')


@admin.register(PricingFAQ)
class PricingFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')


# About Page Admin
@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_description', 'hero_image')
        }),
        ('Story Section', {
            'fields': ('story_title', 'story_subtitle')
        }),
        ('Team Section', {
            'fields': ('team_title',)
        }),
        ('Values Section', {
            'fields': ('values_title',)
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_subtitle')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StorySection)
class StorySectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'content')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'position', 'bio')


@admin.register(CompanyValue)
class CompanyValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('icon', 'order', 'is_active')
    search_fields = ('title', 'description')


# Contact Page Admin
@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle')
        }),
        ('Contact Information', {
            'fields': ('office_address', 'phone_number', 'office_hours', 'email_general', 'email_support')
        }),
        ('Form Section', {
            'fields': ('form_title',)
        }),
        ('Map Section', {
            'fields': ('map_embed_url',)
        }),
        ('FAQ Section', {
            'fields': ('faq_title',)
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_subtitle')
        }),
    )

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactFAQ)
class ContactFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')
