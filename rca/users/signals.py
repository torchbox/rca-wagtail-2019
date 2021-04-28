import logging

from django.db.models.signals import m2m_changed

from rca.people.models import StudentIndexPage, StudentPage

from .models import User

logger = logging.getLogger(__name__)


def do_after_creating_student_user(sender, **kwargs):

    user = kwargs["instance"]

    if user.groups.filter(name="Students").exists():
        try:
            student_index = StudentIndexPage.objects.first()
        except StudentIndexPage.DoesNotExist:
            return

        student_page = StudentPage.objects.filter(
            first_name=user.first_name, last_name=user.last_name,
        ).exists()

        if student_page:
            logger.info(
                "A Student User has been created, but a StudentPage matching "
                f"the users name already exists: {student_page} so one has not been created"
            )
        else:
            student_index.add_child(
                instance=StudentPage(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    title=f"{user.first_name} {user.last_name}",
                    student_user_account=user,
                    live=False,
                )
            )


m2m_changed.connect(do_after_creating_student_user, sender=User.groups.through)
