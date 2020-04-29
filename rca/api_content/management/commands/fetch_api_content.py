from django.core.management.base import BaseCommand

from ...content import AlumniStoriesAPI, NewsEventsAPI


class Command(BaseCommand):
    """Fetch content from the legacy site and store in the cache """

    def handle(self, *args, **options):
        for api in (AlumniStoriesAPI, NewsEventsAPI):
            api().fetch_from_api()
