from django.core.management.base import BaseCommand
from wagtail.models import Page

from rca.people.models import StaffPage
from rca.utils.models import LegacySiteTaggedPage

from ...content import AlumniStoriesAPI, NewsEventsAPI


class Command(BaseCommand):
    """Fetch content from the legacy site and store in the cache"""

    def handle(self, *args, **options):
        for api in (AlumniStoriesAPI, NewsEventsAPI):
            api().fetch_from_api()

        # For all pages with 'legacy_news_and_event_tags' set,
        # populate the cache with related news and events
        for page in Page.objects.filter(
            id__in=LegacySiteTaggedPage.objects.values_list(
                "content_object_id", flat=True
            ).distinct()
        ).specific():
            page.refetch_legacy_news_and_events()

        # Fetch related student data for staff pages
        for page in StaffPage.objects.filter(legacy_staff_id__isnull=False).live():
            page.fetch_related_students()
