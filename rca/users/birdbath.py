from birdbath.processors import BaseProcessor
from django.conf import settings
from faker import Faker

from rca.people.models import StudentPage
from rca.users.models import User


class BaseUserAnonymiser(BaseProcessor):
    def get_queryset(self):
        users = User.objects.all()

        if settings.BIRDBATH_USER_ANONYMISER_EXCLUDE_SUPERUSERS:
            users = users.exclude(is_superuser=True)

        if settings.BIRDBATH_USER_ANONYMISER_EXCLUDE_EMAIL_RE:
            users = users.exclude(
                email__regex=settings.BIRDBATH_USER_ANONYMISER_EXCLUDE_EMAIL_RE
            )

        # Exclude users with an email that matches (end with) @rca.ac.uk
        # Users are all students as they use email addresses ending with @network.rca.ac.uk
        users = users.exclude(email__endswith="@rca.ac.uk")

        return users


class StudentAccountAnonymiser(BaseUserAnonymiser):
    """For all user accounts anonymise the user account +

    1. the student page
    2. the student group name
    3. the student image collection name

    """

    def run(self):
        fake = Faker()
        users = self.get_queryset()

        for count, user in enumerate(users):
            # generate some fake data per user account
            fake_first = fake.first_name()
            fake_last = fake.last_name()
            # count for uniqueness
            fake_username = f"{fake_first}.{fake_last}-{count}".lower()

            self.rename_student_group(user, fake_username)
            self.anonymise_student_page(count, user, fake_first, fake_last)
            self.update_user_account(user, fake_first, fake_last, fake_username)

    def update_user_account(self, user, fake_first, fake_last, fake_username):
        """Update the user account"""
        user.username = fake_username
        user.first_name = fake_first
        user.last_name = fake_last
        user.save()

    def anonymise_student_page(self, count, user, fake_first, fake_last):
        """Anonymise the student page and related image collection name"""
        student_pages = StudentPage.objects.filter(student_user_account=user)
        for student_page in student_pages:

            # change the image collection name to match the student name count is used for uniqueness
            image_collection = student_page.student_user_image_collection
            image_collection.name = f"{fake_first} {fake_last} {count}"
            image_collection.save()

            # change the student page fields so they match the student user account
            # and remove any personal information that may be in the fields
            student_page.title = f"{fake_first} {fake_last}"
            student_page.first_name = fake_first
            student_page.last_name = fake_last
            student_page.email = ""

            rev = student_page.save_revision()
            rev.publish()

    def rename_student_group(self, user, fake_username):
        """Rename the student group to match the student user account"""

        # If a student group begins with Student: then rename it to match the student user account
        student_user_group = None
        for group in user.groups.all():
            if group.name.startswith("Student: "):
                # Student group names are (Student: firstname.lastname)
                group.name = f"Student: {fake_username}"
                # print(group.name)
                group.save()
                student_user_group = group

        if student_user_group:
            student_user_pages = student_user_group.page_permissions.all()
            for student_user_page in student_user_pages:
                student_page = StudentPage.objects.get(id=student_user_page.page_id)
                if student_page.student_user_account == user:
                    student_user_group.name = f"Student: {fake_username}"
                    student_user_group.save()
