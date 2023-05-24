from django.core.management.base import BaseCommand

from teamsite_zoom.tasks import (
    update_all_phone_numbers,
    update_all_phone_users,
    update_all_users,
)


class Command(BaseCommand):
    help = "Fetch Zoom Users"

    def handle(self, *args, **options):
        update_all_users()
        update_all_phone_users()
        update_all_phone_numbers()
