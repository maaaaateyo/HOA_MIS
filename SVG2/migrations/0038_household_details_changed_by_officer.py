# Generated by Django 4.2.11 on 2024-12-08 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0037_grievanceappointment_status_changed_by_officer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='details_changed_by_officer',
            field=models.BooleanField(default=False),
        ),
    ]
