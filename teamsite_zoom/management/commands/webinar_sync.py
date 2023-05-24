from django.core.management.base import BaseCommand

from teamsite_zoom.tasks import api


class Command(BaseCommand):
    help = "Synchronize webinar"

    def add_arguments(self, parser):
        parser.add_argument("webinar_id", type=str)

    def handle(self, *args, webinar_id, **options):
        api.synchronize_webinar_participants(webinar_id)
