# Generated by Django 4.2.11 on 2024-12-08 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0041_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='billing',
            unique_together={('household', 'billing_month')},
        ),
    ]
