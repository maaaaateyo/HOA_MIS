# Generated by Django 4.2.11 on 2024-04-07 08:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SVG2', '0003_alter_household_owner_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='construction',
            field=models.CharField(choices=[('Concrete', 'Concrete'), ('Half Concrete', 'Half Concrete'), ('Nipa', 'Nipa'), ('Wood', 'Wood')], max_length=13),
        ),
        migrations.AlterField(
            model_name='household',
            name='home_tenure',
            field=models.CharField(choices=[('Owner', 'Owner'), ('Renter', 'Renter'), ('Caretaker', 'Caretaker')], max_length=10),
        ),
        migrations.AlterField(
            model_name='household',
            name='kitchen',
            field=models.CharField(choices=[('Shared', 'Shared'), ('Separate', 'Separate')], max_length=10),
        ),
        migrations.AlterField(
            model_name='household',
            name='land_tenure',
            field=models.CharField(choices=[('Owner', 'Owner'), ('Occupant', 'Occupant'), ('Settler', 'Settler')], max_length=10),
        ),
        migrations.AlterField(
            model_name='household',
            name='street',
            field=models.CharField(choices=[('Bellflower', 'Bellflower'), ('Carnation', 'Carnation'), ('Dahlia', 'Dahlia'), ('Daisy', 'Daisy'), ('Gardenia', 'Gardenia'), ('Hyacinth', 'Hyacinth'), ('Petunia', 'Petunia'), ('Poinsettia', 'Poinsettia'), ('Primrose', 'Primrose')], max_length=10),
        ),
        migrations.AlterField(
            model_name='household',
            name='toilet_facility',
            field=models.CharField(choices=[('None', 'None'), ('Open Pit Owned', 'Open Pit Owned'), ('Open Pit Shared', 'Open Pit Shared'), ('Close Pit Owned', 'Close Pit Owned'), ('Close Pit Shared', 'Close Pit Shared'), ('Water Sealed Owned', 'Water Sealed Owned'), ('Water Sealed Shared', 'Water Sealed Shared')], max_length=19),
        ),
        migrations.AlterField(
            model_name='household',
            name='water_facility',
            field=models.CharField(choices=[('Pump', 'Pump'), ('Deepwell', 'Deepwell'), ('Primewater', 'Primewater')], max_length=10),
        ),
        migrations.CreateModel(
            name='Resident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('suffix', models.CharField(blank=True, max_length=10)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('birthdate', models.DateField()),
                ('is_head_of_family', models.BooleanField(default=False)),
                ('relation_to_head', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('contact_number', models.CharField(max_length=15)),
                ('civil_status', models.CharField(choices=[('Single', 'Single'), ('Married', 'Married'), ('Widowed', 'Widowed'), ('Separated', 'Separated'), ('Divorced', 'Divorced')], max_length=10)),
                ('religion', models.CharField(choices=[('Roman Catholic', 'Roman Catholic'), ('Christianity', 'Christianity'), ('Islam', 'Islam'), ('Non-Religious', 'Non-Religious')], max_length=50)),
                ('educational_attainment', models.CharField(choices=[('None', 'None'), ('Elementary', 'Elementary'), ('High School', 'High School'), ('College', 'College'), ('Vocational', 'Vocational'), ('Masters', 'Masters'), ('Doctorate', 'Doctorate')], max_length=50)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='residents', to='SVG2.household')),
            ],
        ),
    ]
