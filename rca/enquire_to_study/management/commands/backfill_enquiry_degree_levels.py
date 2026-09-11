from django.core.management.base import BaseCommand
from django.db.models import OuterRef, Subquery

from rca.enquire_to_study.models import EnquiryFormSubmissionProgrammesOrderable
from rca.programmes.models import ProgrammePage


class Command(BaseCommand):
    """
    Backfill EnquiryFormSubmissionProgrammesOrderable.degree_level from the
    programme's legacy degree_level field, for rows added before that field
    existed. Run manually after deploying migration 0016 (kept as a
    schema-only migration to avoid the release phase timing out on a large
    submissions table), e.g.:

        heroku run python manage.py backfill_enquiry_degree_levels -a <app>
    """

    def handle(self, *args, **options):
        degree_level_subquery = ProgrammePage.objects.filter(
            pk=OuterRef("programme_id")
        ).values("degree_level_id")[:1]

        updated = EnquiryFormSubmissionProgrammesOrderable.objects.filter(
            degree_level__isnull=True,
            programme__degree_level__isnull=False,
        ).update(degree_level=Subquery(degree_level_subquery))

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} rows."))
