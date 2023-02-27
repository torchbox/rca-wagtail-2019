import datetime
import json
import random

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand
from faker import Faker
from wagtail.models import Page

from rca.events.models import (
    EventDetailPage,
    EventDetailPageRelatedDirectorate,
    EventEligibility,
    EventLocation,
    EventSeries,
    EventType,
)
from rca.images.models import CustomImage
from rca.people.models import Directorate
from rca.research.models import RelatedResearchCenterPage, ResearchCentrePage
from rca.schools.models import RelatedSchoolPage, SchoolPage


class Command(BaseCommand):
    """
    IMPORTANT: DO NOT run this on production
    Management command for making example event pages

    ./manage.py make_event_pages [count] [parent_page_id]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.ALLOW_EVENT_PAGE_GENERATION:
            raise ImproperlyConfigured(
                "Creating event pages is disabled, is settings.ALLOW_EVENT_PAGE_GENERATION set correctly?"
            )

    def add_arguments(self, parser):
        parser.add_argument("count", help="How many pages to create")
        parser.add_argument(
            "parent_page_id",
            help="The ID of the parent event listing page",
        )
        parser.add_argument(
            "date",
            help="'past' or 'future' event date",
        )

    def streamfield(self, fake):
        # create a streamfield containing paragraphs and headings
        blocks = []
        for _ in range(random.randrange(3, 5)):
            heading = fake.sentence()[0:-1]
            blocks.append({"type": "heading", "value": heading})
            paragraphs = []
            for _ in range(random.randrange(2, 4)):
                sentences = []
                for _ in range(random.randrange(3, 6)):
                    sentence = fake.sentence(nb_words=random.randrange(7, 17))
                    sentences.append(sentence)
                paragraphs.append(" ".join(sentences))
            paragraph_block = "<p>" + "</p><p>".join(paragraphs) + "</p>"
            blocks.append({"type": "paragraph", "value": paragraph_block})
        return json.dumps(blocks)

    def handle(self, *args, **options):
        fake_index_page = Page.objects.get(id=options["parent_page_id"])
        fake = Faker()
        number_to_create = options["count"]
        date = str(options["date"])

        for _ in range(int(number_to_create)):

            future_date = fake.date_between(start_date="now", end_date="+1y")
            future_dates = {
                "start_date": future_date,
                "end_date": future_date + datetime.timedelta(days=3),
            }
            past_date = fake.date_between(start_date="-7y")
            past_dates = {
                "start_date": past_date,
                "end_date": past_date + datetime.timedelta(days=3),
            }

            # date toggle
            start_date = past_dates["start_date"]
            end_date = past_dates["end_date"]

            if date == "future":
                future_dates["start_date"]
                start_date = future_dates["start_date"]
                end_date = future_dates["end_date"]

            title = " ".join(fake.words(3)).title()
            fake_page = EventDetailPage(
                title=title,
                introduction=fake.sentence(),
                start_date=start_date,
                end_date=end_date,
                body=self.streamfield(fake),
                hero_image_id=CustomImage.objects.order_by("?").first().id,
                event_type=EventType.objects.order_by("?").first(),
                location=EventLocation.objects.order_by("?").first(),
                eligibility=EventEligibility.objects.order_by("?").first(),
                series=EventSeries.objects.order_by("?").first(),
            )
            fake_index_page.add_child(instance=fake_page)

            # School, Centre or Area (directorate)
            schools = RelatedSchoolPage(
                source_page=fake_page, page=SchoolPage.objects.order_by("?").first()
            )
            fake_page.related_schools = [schools]
            research_pages = RelatedResearchCenterPage(
                source_page=fake_page,
                page=ResearchCentrePage.objects.order_by("?").first(),
            )
            fake_page.related_research_centre_pages = [research_pages]

            directorates = EventDetailPageRelatedDirectorate(
                source_page=fake_page,
                directorate=Directorate.objects.order_by("?").first(),
            )
            fake_page.related_directorates = [directorates]

            fake_page.save_revision().publish()
            print("published:" + title)
