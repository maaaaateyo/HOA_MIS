# Generated by Django 4.2.11 on 2024-04-06 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Household',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block', models.CharField(choices=[('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('10', '10')], max_length=50)),
                ('lot', models.CharField(max_length=50)),
                ('street', models.CharField(choices=[('bellflower', 'Bellflower'), ('carnation', 'Carnation'), ('dahlia', 'Dahlia'), ('daisy', 'Daisy'), ('gardenia', 'Gardenia'), ('hyacinth', 'Hyacinth'), ('petunia', 'Petunia'), ('poinsettia', 'Poinsettia'), ('primrose', 'Primrose')], max_length=10)),
                ('home_tenure', models.CharField(choices=[('owner', 'Owner'), ('renter', 'Renter'), ('caretaker', 'Caretaker')], max_length=10)),
                ('land_tenure', models.CharField(choices=[('owner', 'Owner'), ('occupant', 'Occupant'), ('settler', 'Settler')], max_length=10)),
                ('construction', models.CharField(choices=[('concrete', 'Concrete'), ('half concrete', 'Half Concrete'), ('nipa', 'Nipa'), ('wood', 'Wood')], max_length=13)),
                ('vehicles_owned', models.TextField(blank=True, null=True)),
                ('kitchen', models.CharField(choices=[('shared', 'Shared'), ('separate', 'Separate')], max_length=10)),
                ('water_facility', models.CharField(choices=[('pump', 'Pump'), ('deepwell', 'Deepwell'), ('primewater', 'Primewater')], max_length=10)),
                ('toilet_facility', models.CharField(choices=[('none', 'None'), ('open pit owned', 'Open Pit Owned'), ('open pit shared', 'Open Pit Shared'), ('close pit owned', 'Close Pit Owned'), ('close pit shared', 'Close Pit Shared'), ('water sealed owned', 'Water Sealed Owned'), ('water sealed shared', 'Water Sealed Shared')], max_length=19)),
                ('owner_name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
