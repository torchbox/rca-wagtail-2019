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

        return users


class StudentAccountAnonymiser(BaseUserAnonymiser):
    """Anonymise student accounts"""

    def run(self):
        fake = Faker()
        users = self.get_queryset()

        for count, user in enumerate(users):
            # generate some fake data per user account
            fake_first = fake.first_name()
            fake_last = fake.last_name()
            fake_username = f"{fake_first}-{fake_last}-{count}".lower()
            fake_email = f"{fake_first.lower()}.{fake_last.lower()}@example.com"
            fake_words = " ".join(fake.words(10))
            fake_url = "http://www.example.com"

            self.rename_student_group(user, fake_username)
            self.anonymise_student_page(
                count, user, fake_first, fake_last, fake_email, fake_words, fake_url
            )
            self.update_user_account(
                user, fake_first, fake_last, fake_username, fake_email
            )

    def update_user_account(
        self, user, fake_first, fake_last, fake_username, fake_email
    ):
        """Update the user account"""
        user.username = fake_username
        user.first_name = fake_first
        user.last_name = fake_last
        user.email = fake_email
        user.save()

    def anonymise_student_page(
        self, count, user, fake_first, fake_last, fake_email, fake_words, fake_url
    ):
        """Anonymise the student page and related information"""
        student_pages = StudentPage.objects.filter(student_user_account=user)
        for student_page in student_pages:

            # change the image collection name to match the student name count is used for uniqueness
            image_collection = student_page.student_user_image_collection
            image_collection.name = f"{fake_first} {fake_last} {count}"
            image_collection.save()

            # remove related personal links and related links inline records
            student_page.personal_links.all().delete()
            student_page.relatedlinks.all().delete()

            # change the student page fields so they match the student user account
            # and remove any personal information that may be in the fields
            student_page.title = f"{fake_first} {fake_last}"
            student_page.first_name = fake_first
            student_page.last_name = fake_last
            student_page.profile_image = None
            student_page.email = fake_email
            student_page.introduction = fake_words
            student_page.bio = fake_words
            student_page.biography = fake_words
            student_page.degrees = fake_words
            student_page.experience = fake_words
            student_page.awards = fake_words
            student_page.funding = fake_words
            student_page.exhibitions = fake_words
            student_page.publications = fake_words
            student_page.research_outputs = fake_words
            student_page.conferences = fake_words
            student_page.additional_information_title = fake_words
            student_page.addition_information_content = fake_words
            student_page.link_to_final_thesis = fake_url
            student_page.student_funding = f"<p>{fake_words}</p>"

            rev = student_page.save_revision()
            rev.publish()

    def rename_student_group(self, user, fake_username):
        """Rename the student group to match the student user account"""

        # a student can have multiple groups selected.
        # Here the intention to only change the single student group for a user that has
        # the correct page edit permissions
        student_user_group = (
            user.groups.all().exclude(name="Students").exclude(name="Editors").first()
        )
        if (
            student_user_group
            and student_user_group.name == f"Student: {user.username}"
        ):
            student_user_pages = student_user_group.page_permissions.all()
            for student_user_page in student_user_pages:
                student_page = StudentPage.objects.get(id=student_user_page.page_id)
                if student_page.student_user_account == user:
                    student_user_group.name = f"Student: {fake_username}"
                    student_user_group.save()


class UserPasswordAnonymiser(BaseUserAnonymiser):
    """Anonymise user passwords"""

    def run(self):
        fake = Faker()
        users = self.get_queryset()

        for user in users:
            user.set_password(
                fake.password(
                    length=8,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                )
            )

        User.objects.bulk_update(users, ["password"], batch_size=100)
