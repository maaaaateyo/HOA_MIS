
from django.core.management.base import BaseCommand
from myapp.models import Reservation

class Command(BaseCommand):
    help = 'Cancel expired pending reservations'

    def handle(self, *args, **kwargs):
        expired_reservations = Reservation.cancel_expired_reservations()
        self.stdout.write(f"Canceled {expired_reservations.count()} expired pending reservations.")