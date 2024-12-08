from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from SVG2.models import Household, Billing  # Update 'yourapp' to your actual app name

class Command(BaseCommand):
    help = 'Generates monthly billing records for all households'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)
        monthly_dues_amount = Decimal('100.00')  # Adjust this amount as necessary

        # Iterate through all households instead of users
        households = Household.objects.all()

        for household in households:
            # Check if a billing record for the current month already exists for this household
            if not Billing.objects.filter(household=household, billing_month=first_day_of_month).exists():
                Billing.objects.create(
                    household=household,
                    billing_month=first_day_of_month,
                    amount=monthly_dues_amount,
                    status='Unpaid'  # Ensure this matches the choices in your Billing model
                )
                self.stdout.write(self.style.SUCCESS(f'Generated billing for household {household}'))

        self.stdout.write(self.style.SUCCESS('Monthly billing records generation complete.'))
