import json
from datetime import date, time

import wagtail_factories
from wagtail.test.utils import WagtailPageTestCase

from rca.events.factories import (
    EventAvailabilityFactory,
    EventDetailPageFactory,
    EventEligibilityFactory,
    EventLocationFactory,
    EventTypeFactory,
)
from rca.events.models import (
    EventDetailPageEventType,
    EventDetailPageRelatedDirectorate,
    EventDetailPageRelatedPages,
    EventDetailPageSpeaker,
)
from rca.home.models import HomePage
from rca.people.factories import DirectorateFactory, StaffPageFactory
from rca.people.models import Directorate
from rca.programmes.factories import ProgrammePageFactory
from rca.schools.factories import SchoolPageFactory
from rca.schools.models import RelatedSchoolPage


class EventAPIResponseTest(WagtailPageTestCase):
    """The RCA intranet import tool relies on the structure
    of this API response, so it's covered with a test to ensure
    that should the structure change, we are alerted about it as
    it will break the importer on the intranet"""

    def setUp(self):
        # Created models for FK relationships
        self.event_type = EventTypeFactory(title="party")
        self.directorate = DirectorateFactory(title="ufos", intranet_slug="u-f-o-s")
        self.programme_one = ProgrammePageFactory(
            title="How to draw Aliens", intranet_slug="htd-aliens"
        )
        self.programme_two = ProgrammePageFactory(
            title="How to erase Aliens", intranet_slug="hte-aliens"
        )
        self.related_event = EventDetailPageFactory(title="Alien xmas")
        self.staff_one = StaffPageFactory()
        self.staff_two = StaffPageFactory()
        self.school_one = SchoolPageFactory(
            title="School one",
            intranet_slug="school-one",
            introduction_image=wagtail_factories.ImageFactory(),
        )
        self.school_two = SchoolPageFactory(
            title="School two",
            intranet_slug="school-two",
            introduction_image=wagtail_factories.ImageFactory(),
        )

        self.home_page = HomePage.objects.first()
        self.event_page = EventDetailPageFactory(
            parent=self.home_page,
            introduction="Welcome, to the introduction",
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 6),
            start_time=time(9, 15),
            end_time=time(17, 45),
            location=EventLocationFactory(title="Roswell"),
            availability=EventAvailabilityFactory(title="Tickets still available"),
            eligibility=EventEligibilityFactory(title="Aliens only"),
            contact_model_email="fox.mulder@fbi.com",
            hero_image=wagtail_factories.ImageFactory(),
            listing_image=wagtail_factories.ImageFactory(title="The listing image"),
            listing_title="The listing title",
            listing_summary="A summary for listing",
            manual_registration_url_link_text="Register now",
            manual_registration_url="https://rca.ac.uk/register",
            event_cost="$100",
            body=json.dumps(
                [
                    {"type": "heading", "value": "the heading"},
                    {"type": "image", "value": wagtail_factories.ImageFactory().pk},
                    {"type": "paragraph", "value": "<p>A paragraph</p>"},
                    {"type": "embed", "value": "https://rca.ac.uk"},
                    {
                        "type": "quote",
                        "value": {
                            "quote": "the quote",
                            "author": "the author",
                            "job_title": "publsiher",
                        },
                    },
                ]
            ),
        )

        self.event_page.event_types = [
            EventDetailPageEventType(
                source_page=self.event_page,
                event_type=self.event_type,
            )
        ]

        self.event_page.related_directorates = [
            EventDetailPageRelatedDirectorate(
                source_page=self.event_page, directorate=self.directorate
            )
        ]
        self.event_page.related_pages = [
            EventDetailPageRelatedPages(
                source_page=self.event_page, page=self.programme_one, sort_order=1
            ),
            EventDetailPageRelatedPages(
                source_page=self.event_page, page=self.programme_two, sort_order=2
            ),
            EventDetailPageRelatedPages(
                source_page=self.event_page, page=self.related_event, sort_order=3
            ),
        ]
        self.event_page.speakers = [
            EventDetailPageSpeaker(
                source_page=self.event_page, page=self.staff_one, sort_order=1
            ),
            EventDetailPageSpeaker(
                source_page=self.event_page, page=self.staff_two, sort_order=2
            ),
            EventDetailPageSpeaker(
                source_page=self.event_page,
                first_name="Lister",
                surname="Red",
                link="https://rca.ac.uk/lister",
                sort_order=3,
            ),
        ]
        self.event_page.related_schools = [
            RelatedSchoolPage(
                source_page=self.event_page, page=self.school_one, sort_order=1
            ),
            RelatedSchoolPage(
                source_page=self.event_page, page=self.school_two, sort_order=2
            ),
        ]
        self.event_page.save()

    def test_event_response(self):
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")

        self.assertEqual(response.data["introduction"], "Welcome, to the introduction")
        self.assertEqual(response.data["location"]["title"], "Roswell")
        self.assertEqual(
            response.data["availability"]["title"], "Tickets still available"
        )
        self.assertEqual(response.data["eligibility"]["title"], "Aliens only")
        self.assertEqual(
            response.data["contact_email"], [{"email_address": "fox.mulder@fbi.com"}]
        )
        self.assertEqual(
            response.data["dates_times"],
            [
                {
                    "date_from": "2021-01-06",
                    "date_to": "2021-01-06",
                    "time_from": "09:15:00",
                    "time_to": "17:45:00",
                }
            ],
        )
        self.assertEqual(
            response.data["related_directorates"],
            [{"title": "ufos", "id": self.directorate.id, "intranet_slug": "u-f-o-s"}],
        )
        self.assertEqual(
            response.data["event_types"], [{"id": self.event_type.id, "title": "party"}]
        )
        self.assertEqual(
            response.data["related_programmes"],
            [
                {
                    "page": {
                        "title": "How to draw Aliens",
                        "id": self.programme_one.id,
                        "slug": "how-to-draw-aliens",
                        "intranet_slug": "htd-aliens",
                    }
                },
                {
                    "page": {
                        "title": "How to erase Aliens",
                        "id": self.programme_two.id,
                        "slug": "how-to-erase-aliens",
                        "intranet_slug": "hte-aliens",
                    }
                },
            ],
        )
        self.assertEqual(
            response.data["speakers"][0]["first_name_api"], self.staff_one.first_name
        )
        self.assertEqual(
            response.data["speakers"][0]["surname_api"], self.staff_one.last_name
        )
        self.assertEqual(response.data["speakers"][0]["link_or_page"], None)
        self.assertEqual(
            response.data["speakers"][1]["first_name_api"], self.staff_two.first_name
        )
        self.assertEqual(
            response.data["speakers"][1]["surname_api"], self.staff_two.last_name
        )
        self.assertEqual(response.data["speakers"][1]["link_or_page"], None)
        self.assertEqual(response.data["speakers"][2]["first_name_api"], "Lister")
        self.assertEqual(response.data["speakers"][2]["surname_api"], "Red")
        self.assertEqual(
            response.data["speakers"][2]["link_or_page"], "https://rca.ac.uk/lister"
        )
        self.assertEqual(
            response.data["related_schools"][0]["page"]["title"], "School one"
        )
        self.assertEqual(
            response.data["related_schools"][0]["page"]["intranet_slug"], "school-one"
        )
        self.assertEqual(
            response.data["related_schools"][1]["page"]["title"], "School two"
        )
        self.assertEqual(
            response.data["related_schools"][1]["page"]["intranet_slug"], "school-two"
        )
        self.assertEqual(
            response.data["listing_title"],
            "The listing title",
        )
        self.assertEqual(response.data["listing_summary"], "A summary for listing")
        self.assertEqual(response.data["listing_image"]["title"], "The listing image")
        self.assertEqual(len(self.event_page.body), 5)
        self.assertEqual(
            response.data["manual_registration_url_link_text"], "Register now"
        )
        self.assertEqual(
            response.data["manual_registration_url"], "https://rca.ac.uk/register"
        )
        self.assertEqual(response.data["event_cost"], "$100")


class EventSerializerTests(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        event_type = EventTypeFactory()
        self.event_page = EventDetailPageFactory(
            parent=self.home_page,
        )
        EventDetailPageEventType.objects.create(
            event_type=event_type, source_page=self.event_page
        )

    def test_api_response_for_event(self):
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)

    def test_api_response_for_event_with_null_type(self):
        for et in self.event_page.event_types.all():
            et.event_type.delete()
        self.event_page.refresh_from_db()
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["event_types"], [])

    def test_api_response_for_event_with_null_directorate(self):
        # Add a directorate that relates to the page
        directorate = DirectorateFactory()
        self.event_page.related_directorates = [
            EventDetailPageRelatedDirectorate(
                source_page=self.event_page, directorate=directorate
            )
        ]
        self.event_page.save()
        # Check the directorate is there
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["related_directorates"][0]["title"], directorate.title
        )

        # Delete the directorate
        directorate = Directorate.objects.get(
            id=self.event_page.related_directorates.first().directorate.id
        )
        directorate.delete()

        # Assert there are no related directorates
        self.assertQuerySetEqual(self.event_page.related_directorates.all(), [])
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["related_directorates"], [])


# TODO
# The intranet integration depends on the api structure remaining intact.
# we need to write tests to confirm it fails if changed
