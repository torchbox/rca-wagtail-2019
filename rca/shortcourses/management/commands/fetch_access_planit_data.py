import logging

from django.core.management import BaseCommand

from rca.shortcourses.access_planit import AccessPlanitXML
from rca.shortcourses.models import ShortCoursePage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetches data for each short course page from AccessPlanit XML feed and places it in the cache"

    def handle(self, **options):
        short_courses = ShortCoursePage.objects.all()
        logger.info(f"Fetching AccessPlanit data for Short Coures pages")
        for course in short_courses:
            ap_data = AccessPlanitXML(course_id=course.access_planit_course_id)
            ap_data.set_data_in_cache()
