# Generated by Django 4.2.11 on 2024-04-10 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0012_alter_member_user_alter_officer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='officer_position',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]