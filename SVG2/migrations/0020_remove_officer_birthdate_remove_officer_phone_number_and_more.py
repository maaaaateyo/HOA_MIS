# Generated by Django 4.2.11 on 2024-04-12 06:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0019_officer_birthdate_officer_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='officer',
            name='birthdate',
        ),
        migrations.RemoveField(
            model_name='officer',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='officer',
            name='profile_picture',
        ),
    ]
