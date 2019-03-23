from django.conf import settings
from django.core.management.base import BaseCommand

from mainapp.models import Travler


class Command(BaseCommand):
    help = 'Create superuser'

    def handle(self, *args, **options):
        username = settings.CONFIG.get('SUPERUSER_NAME', 'travl')
        _superuser = Travler.objects.filter(username=username).first()
        if not _superuser:
            Travler.objects.create_superuser(
                username=username,
                email=settings.CONFIG.get('SUPERUSER_MAIL', 'example@example.local'),
                password=settings.CONFIG.get('SUPERUSER_WORD', 'h28P1986'),
                info=""
            )
            print("Added superuser")
        else:
            print("Superuser exists")
