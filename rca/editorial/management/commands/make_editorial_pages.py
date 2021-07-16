import json
import random

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand
from faker import Faker
from wagtail.core.models import Page

from rca.editorial.models import EditorialPage
from rca.images.models import CustomImage


class Command(BaseCommand):
    """
    IMPORTANT: DO NOT run this on production
    Management command for making example editorial pages

    ./manage.py make_editorial_pages [count] [parent_page_id]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.ALLOW_EDITORIAL_PAGE_GENERATION:
            raise ImproperlyConfigured(
                "Creating editorial pages is disabled, is settings.ALLOW_EDITORIAL_PAGE_GENERATION set correctly?"
            )

    def add_arguments(self, parser):
        parser.add_argument("count", help="How many pages to create")
        parser.add_argument(
            "parent_page_id", help="The ID of the parent editorial listing page",
        )

    def streamfield(self, fake):
        # create a streamfield containing paragraphs and headings
        blocks = []
        for _ in range(random.randrange(3, 5)):
            heading = fake.sentence()[0:-1]
            blocks.append({u"type": u"heading", u"value": heading})
            paragraphs = []
            for _ in range(random.randrange(2, 4)):
                sentences = []
                for _ in range(random.randrange(3, 6)):
                    sentence = fake.sentence(nb_words=random.randrange(7, 17))
                    sentences.append(sentence)
                paragraphs.append(" ".join(sentences))
            paragraph_block = "<p>" + "</p><p>".join(paragraphs) + "</p>"
            blocks.append({u"type": u"paragraph", u"value": paragraph_block})
        return json.dumps(blocks)

    def handle(self, *args, **options):
        fake_index_page = Page.objects.get(id=options["parent_page_id"])
        fake = Faker()
        number_to_create = options["count"]
        for _ in range(int(number_to_create)):
            title = " ".join(fake.words(3)).title()
            fake_page = EditorialPage(
                title=title,
                introduction=fake.sentence(),
                published_at=fake.date(),
                body=self.streamfield(fake),
                hero_image_id=CustomImage.objects.order_by("?").first().id,
            )
            fake_index_page.add_child(instance=fake_page)
            fake_page.save_revision().publish()
            print("published:" + title)
