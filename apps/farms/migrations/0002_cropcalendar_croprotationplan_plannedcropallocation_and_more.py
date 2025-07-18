# Generated by Django 5.2 on 2025-06-22 12:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CropCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('planting', 'Planting'), ('fertilizing', 'Fertilizing'), ('weeding', 'Weeding'), ('watering', 'Watering'), ('pest_control', 'Pest Control'), ('pruning', 'Pruning'), ('harvesting', 'Harvesting'), ('soil_preparation', 'Soil Preparation'), ('maintenance', 'Maintenance'), ('other', 'Other')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_recurring', models.BooleanField(default=False)),
                ('recurrence_pattern', models.CharField(blank=True, max_length=50)),
                ('recurrence_interval', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('overdue', 'Overdue')], default='planned', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=20)),
                ('weather_dependent', models.BooleanField(default=False)),
                ('min_temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('max_temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('max_wind_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('no_rain_required', models.BooleanField(default=False)),
                ('estimated_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('actual_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('completion_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_calendar_events', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_calendar_events', to=settings.AUTH_USER_MODEL)),
                ('crop_cycle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='calendar_events', to='farms.cropcycle')),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calendar_events', to='farms.farm')),
            ],
            options={
                'ordering': ['start_date', 'priority'],
            },
        ),
        migrations.CreateModel(
            name='CropRotationPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_name', models.CharField(max_length=255)),
                ('rotation_cycle_years', models.PositiveIntegerField(default=3)),
                ('soil_health_benefits', models.TextField(blank=True)),
                ('pest_management_benefits', models.TextField(blank=True)),
                ('economic_benefits', models.TextField(blank=True)),
                ('start_year', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_plans', to=settings.AUTH_USER_MODEL)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_plans', to='farms.farm')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_plans', to='farms.farmsection')),
                ('year_1_crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_year_1', to='farms.crop')),
                ('year_2_crop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rotation_year_2', to='farms.crop')),
                ('year_3_crop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rotation_year_3', to='farms.crop')),
                ('year_4_crop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rotation_year_4', to='farms.crop')),
            ],
        ),
        migrations.CreateModel(
            name='PlannedCropAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocated_area', models.DecimalField(decimal_places=2, max_digits=10)),
                ('expected_yield_per_hectare', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('planned_planting_date', models.DateField()),
                ('planned_harvest_date', models.DateField()),
                ('estimated_cost_per_hectare', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('expected_price_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('notes', models.TextField(blank=True)),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farms.crop')),
                ('crop_variety', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='farms.cropvariety')),
            ],
        ),
        migrations.CreateModel(
            name='SeasonalPlanning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season_year', models.PositiveIntegerField()),
                ('season', models.CharField(choices=[('spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall'), ('winter', 'Winter'), ('wet', 'Wet Season'), ('dry', 'Dry Season')], max_length=20)),
                ('planning_notes', models.TextField(blank=True)),
                ('soil_prep_required', models.BooleanField(default=True)),
                ('irrigation_plan', models.TextField(blank=True)),
                ('fertilization_plan', models.TextField(blank=True)),
                ('estimated_total_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('estimated_revenue', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('approved', 'Approved'), ('active', 'Active'), ('completed', 'Completed')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasonal_plans', to=settings.AUTH_USER_MODEL)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasonal_plans', to='farms.farm')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasonal_plans', to='farms.farmsection')),
                ('planned_crops', models.ManyToManyField(through='farms.PlannedCropAllocation', to='farms.crop')),
            ],
            options={
                'ordering': ['-season_year', 'season'],
                'unique_together': {('field', 'season_year', 'season')},
            },
        ),
        migrations.AddField(
            model_name='plannedcropallocation',
            name='seasonal_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farms.seasonalplanning'),
        ),
    ]
