# Generated by Django 4.2.11 on 2024-11-15 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0033_notification_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='household',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='SVG2.household'),
        ),
    ]
