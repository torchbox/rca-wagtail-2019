from birdbath.processors import BaseModelAnonymiser
from faker import Faker

from rca.people.models import StudentPage


class StudentPageAnonymiser(BaseModelAnonymiser):
    model = StudentPage

    def run(self):
        fake = Faker()
        for student_page in self.get_queryset():
            first_name = fake.first_name()
            last_name = fake.last_name()
            page_title = f"{first_name} {last_name}"
            student_page.title = page_title
            student_page.first_name = first_name
            student_page.last_name = last_name
            student_page.email = f"{first_name}.{last_name}@example.com"
            rev = student_page.save_revision()
            rev.publish()

            student_page_user = student_page.student_user_account
            student_page_user.set_password(self.get_random_string())
