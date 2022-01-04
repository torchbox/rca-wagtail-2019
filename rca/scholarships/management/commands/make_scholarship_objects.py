import factory
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand

from rca.scholarships.factories import ScholarshipFactory


class Command(BaseCommand):
    """
    IMPORTANT: DO NOT run this on production
    Management command for making example scholarship objects

    ./manage.py make_scholarship_objects [count]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.DEBUG:
            raise ImproperlyConfigured(
                "Creating scholarship objects is disabled when `DEBUG=False`."
            )

    def add_arguments(self, parser):
        parser.add_argument("count", help="How many scholarships to create")

    def handle(self, *args, **options):
        ScholarshipFactory.generate_batch(
            strategy=factory.CREATE_STRATEGY, size=int(options["count"])
        )
