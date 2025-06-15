from django.contrib import admin
from .models import Farm, FarmSection, Crop, CropVariety, CropCycle, SoilTest, WeatherRecord

# Register Farm models
@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'farm_type', 'location', 'size', 'is_active')
    list_filter = ('farm_type', 'is_active')
    search_fields = ('name', 'owner__username', 'location')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FarmSection)
class FarmSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'size', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'farm__name')

# Register Crop models
@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name', 'growing_season', 'average_growing_period_days')
    search_fields = ('name', 'scientific_name')
    list_filter = ('growing_season',)

@admin.register(CropVariety)
class CropVarietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'crop', 'maturity_days', 'yield_potential')
    list_filter = ('crop',)
    search_fields = ('name', 'crop__name')

@admin.register(CropCycle)
class CropCycleAdmin(admin.ModelAdmin):
    list_display = ('crop', 'field', 'planting_date', 'expected_harvest_date', 'status')
    list_filter = ('status', 'crop', 'planting_date')
    search_fields = ('crop__name', 'field__name')
    date_hierarchy = 'planting_date'

# Register other farm-related models
@admin.register(SoilTest)
class SoilTestAdmin(admin.ModelAdmin):
    list_display = ('field', 'test_date', 'ph', 'nitrogen_ppm', 'phosphorus_ppm', 'potassium_ppm')
    list_filter = ('test_date',)
    date_hierarchy = 'test_date'

@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ('farm', 'date', 'temperature_max', 'temperature_min', 'rainfall_mm')
    list_filter = ('date', 'data_source')
    date_hierarchy = 'date'
