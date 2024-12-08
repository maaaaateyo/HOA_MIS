# Generated by Django 4.2.11 on 2024-04-09 10:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0006_alter_reservation_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('service_type', models.CharField(choices=[('Maintenance', 'Maintenance Request'), ('Incident', 'Incident Report')], default='maintenance', max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='service_requests/')),
                ('status', models.CharField(choices=[('Submitted', 'Submitted'), ('In_progress', 'In Progress'), ('Completed', 'Completed')], default='Submitted', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]