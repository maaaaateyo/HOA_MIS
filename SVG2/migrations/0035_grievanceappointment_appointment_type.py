# Generated by Django 4.2.11 on 2024-12-05 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0034_alter_notification_household'),
    ]

    operations = [
        migrations.AddField(
            model_name='grievanceappointment',
            name='appointment_type',
            field=models.CharField(choices=[('Get HOA Certificate', 'Get HOA Certificate'), ('Grievance', 'Grievance'), ('Others', 'Others')], default='HOA Certification', max_length=20),
        ),
    ]
