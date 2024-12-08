# Generated by Django 4.2.11 on 2024-04-13 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0023_alter_officer_officer_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('who', models.CharField(max_length=200)),
                ('what', models.TextField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('where', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='announcements_images/')),
            ],
        ),
    ]