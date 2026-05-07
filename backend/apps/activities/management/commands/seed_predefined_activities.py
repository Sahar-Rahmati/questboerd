from django.core.management.base import BaseCommand

from apps.activities.services import seed_predefined_activities


class Command(BaseCommand):
    help = "Seed the predefined activity bank."

    def handle(self, *args, **options):
        created = seed_predefined_activities()
        self.stdout.write(self.style.SUCCESS(f"Seeded activities. Newly created: {created}"))
