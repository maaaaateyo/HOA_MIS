# Generated by Django 4.2.11 on 2024-04-11 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0015_rename_news_newsfeed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Denied', 'Denied'), ('Canceled', 'Canceled')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='resident',
            name='birthdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('Submitted', 'Submitted'), ('In_progress', 'In Progress'), ('Completed', 'Completed'), ('Canceled', 'Canceled')], default='Submitted', max_length=20),
        ),
    ]
