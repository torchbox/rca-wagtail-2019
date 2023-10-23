import json

import wagtail_factories
from wagtail.test.utils import WagtailPageTestCase

from rca.editorial.factories import (
    AuthorFactory,
    EditorialPageFactory,
    EditorialTypeFactory,
)
from rca.editorial.models import (
    EditorialPageDirectorate,
    EditorialPageRelatedProgramme,
    EditorialPageTypePlacement,
    EditorialType,
)
from rca.home.models import HomePage
from rca.people.factories import DirectorateFactory
from rca.programmes.factories import ProgrammePageFactory
from rca.schools.factories import SchoolPageFactory
from rca.schools.models import RelatedSchoolPage


class EditorialPageAPIResponseTest(WagtailPageTestCase):
    """The RCA intranet import tool relies on the structure
    of this API response, so it's covered with a test to ensure
    that should the structure change, we are alerted about it as
    it will break the importer on the intranet"""

    def setUp(self):
        # Created models for FK relationships
        self.directorate = DirectorateFactory(title="ufos", intranet_slug="u-f-o-s")
        self.programme_one = ProgrammePageFactory(
            title="How to draw Aliens", intranet_slug="htd-aliens"
        )
        self.programme_two = ProgrammePageFactory(
            title="How to erase Aliens", intranet_slug="hte-aliens"
        )
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
        editorial_type = EditorialTypeFactory(title="Alien news")

        self.home_page = HomePage.objects.first()
        self.editorial_page = EditorialPageFactory(
            parent=self.home_page,
            introduction="An introduction for the editorial page",
            hero_image=wagtail_factories.ImageFactory(),
            listing_image=wagtail_factories.ImageFactory(title="The listing image"),
            contact_email="fox.mulder@fbi.com",
            listing_title="The listing title",
            listing_summary="A summary for listing",
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
            cta_block=json.dumps(
                [
                    {
                        "type": "call_to_action",
                        "value": {
                            "title": "The CTA title",
                            "description": "A CTA description",
                            "link": {
                                "title": "A link",
                                "url": "https//rca.ac.uk/ctalink",
                            },
                            "page": None,
                        },
                    }
                ],
            ),
            author=AuthorFactory(name="Dana Scully"),
        )
        self.editorial_page.editorial_types = [
            EditorialPageTypePlacement(page=self.editorial_page, type=editorial_type)
        ]
        self.editorial_page.related_schools = [
            RelatedSchoolPage(source_page=self.editorial_page, page=self.school_one),
            RelatedSchoolPage(source_page=self.editorial_page, page=self.school_two),
        ]
        self.editorial_page.related_directorates = [
            EditorialPageDirectorate(
                page=self.editorial_page, directorate=self.directorate
            )
        ]
        self.editorial_page.related_programmes = [
            EditorialPageRelatedProgramme(
                source_page=self.editorial_page, page=self.programme_one
            ),
            EditorialPageRelatedProgramme(
                source_page=self.editorial_page, page=self.programme_two
            ),
        ]
        self.editorial_page.save()

    def test_editorial_response(self):
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(
            response.data["listing_title"],
            "The listing title",
        )
        self.assertEqual(response.data["listing_summary"], "A summary for listing")
        self.assertEqual(response.data["listing_image"]["title"], "The listing image")
        self.assertEqual(
            response.data["introduction"], "An introduction for the editorial page"
        )
        self.assertEqual(len(self.editorial_page.body), 5)
        self.assertEqual(
            response.data["published_at"],
            self.editorial_page.published_at.strftime("%Y-%m-%d"),
        )
        self.assertEqual(response.data["contact_email"], "fox.mulder@fbi.com")
        self.assertEqual(
            response.data["related_directorates"],
            [{"title": "ufos", "id": self.directorate.id, "intranet_slug": "u-f-o-s"}],
        )
        self.assertEqual(
            response.data["related_programmes_api"],
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
        self.assertEqual(response.data["author_as_string"], "Dana Scully")
        self.assertEqual(response.data["editorial_types"][0]["title"], "Alien news")


class EditorialSerializerTests(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.editorial_page = EditorialPageFactory(
            parent=self.home_page,
        )

    def test_api_response_for_editorial(self):
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)

    def test_api_response_for_editorial_with_type(self):
        editorial_type = EditorialTypeFactory()
        self.editorial_page.editorial_types = [
            EditorialPageTypePlacement(page=self.editorial_page, type=editorial_type)
        ]
        self.editorial_page.save()
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)
        # Check the directorate is there
        self.assertEqual(
            response.data["editorial_types"][0]["title"], editorial_type.title
        )

    def test_api_response_for_editorial_with_deleted_type(self):
        editorial_type = EditorialTypeFactory()
        self.editorial_page.editorial_types = [
            EditorialPageTypePlacement(page=self.editorial_page, type=editorial_type)
        ]
        self.editorial_page.save()
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)
        # Check the directorate is there
        self.assertEqual(
            response.data["editorial_types"][0]["title"], editorial_type.title
        )

        # Delete the type
        type = EditorialType.objects.get(
            id=self.editorial_page.editorial_types.first().type.id
        )
        type.delete()
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)
        # Check the directorate is there
        self.assertEqual(response.data["editorial_types"], [])
