# Generated by Django 4.2.11 on 2024-04-08 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0005_reservation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]