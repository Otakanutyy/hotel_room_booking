from django.core.management.base import BaseCommand

from rooms.models import Room


class Command(BaseCommand):
    help = "Seed a small set of sample rooms (idempotent)."

    def handle(self, *args, **options):
        sample_rooms = [
            {"name": "101", "price_per_night": "80.00", "capacity": 1},
            {"name": "102", "price_per_night": "120.00", "capacity": 2},
            {"name": "201", "price_per_night": "150.00", "capacity": 2},
            {"name": "202", "price_per_night": "220.00", "capacity": 4},
        ]

        created_count = 0
        for data in sample_rooms:
            _, created = Room.objects.get_or_create(name=data["name"], defaults=data)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"seed_rooms: created {created_count} room(s)"))
