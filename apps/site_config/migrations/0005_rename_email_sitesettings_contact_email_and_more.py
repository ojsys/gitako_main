# Generated by Django 5.2 on 2025-04-14 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_config', '0004_rename_maintenance_message_sitesettings_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sitesettings',
            old_name='email',
            new_name='contact_email',
        ),
        migrations.RenameField(
            model_name='sitesettings',
            old_name='phone',
            new_name='contact_phone',
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='footer_text',
            field=models.CharField(default='© Gitako. All rights reserved.', max_length=200),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='maintenance_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='maintenance_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='favicon',
            field=models.ImageField(blank=True, null=True, upload_to='site/favicon/'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='hero_subtitle',
            field=models.TextField(default='Gitako helps you manage your farm operations efficiently, track activities, monitor inventory, and maximize profits with data-driven insights.'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='hero_title',
            field=models.CharField(default='Smart Farm Management', max_length=200),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='site/logo/'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='meta_keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='site_name',
            field=models.CharField(default='Gitako', max_length=100),
        ),
    ]
