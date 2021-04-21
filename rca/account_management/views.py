import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from wagtail.admin import messages

from rca.people.models import StudentIndexPage, StudentPage
from rca.users.models import User

from .forms import StudentCreateForm
from .utils import get_set_password_url

logger = logging.getLogger(__name__)


class CreateStudentFormView(FormView):
    """Custom admin form for creating student user accounts.

    The form allows administrators to add student accounts with the option of
    creating a rca.people.models.StudentPage object related to the user through
    StudentPage.student_user_account.

    Student accounts can be created without adding a StudentPage, this is controled
    by a boolean on StudentCreateForm.create_student_page.
    """

    template_name = "account_management/create.html"
    form_class = StudentCreateForm
    success_url = "/admin/student/create"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super(CreateStudentFormView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = super().form_valid(form)
        # Create the student account
        student_group = Group.objects.get(name="Students")
        student_user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        )
        # Add the student group
        student_user.groups.add(student_group)
        student_user.set_unusable_password()
        student_user.save()

        # return here if we aren't creating a page for the student
        if not form.cleaned_data["create_student_page"]:
            messages.success(
                self.request,
                f"The Student account for {student_user} has been created.",
            )
            return data

        # Is there a student index page we can create a student page under?
        student_index = StudentIndexPage.objects.first()
        if not student_index:
            messages.warning(
                self.request,
                f"Failed to create a Student Page matching for the new user: {student_user}, "
                "a Parent Student Index Page is required.",
            )
            logger.info(
                "There is not parent Student Index page to create a Student Page under, "
                f"so one has not been created for user: {student_user}"
            )
            return data

        # If a student page already exist for this user, we don't want to create one.
        student_page = StudentPage.objects.filter(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        ).exists()

        if student_page:
            messages.success(
                self.request,
                f"The Student account for {student_user} has been created.",
            )
            messages.warning(
                self.request,
                f"Failed to create a Student Page matching for the new user: {student_user}, "
                "a Student Page already already exists",
            )
            logger.info(
                "A Student User has been created, but a StudentPage matching "
                f"the users name already exists: {student_page}, so one has not been created"
            )
        else:
            student_index.add_child(
                instance=StudentPage(
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    title=f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
                    student_user_account=student_user,
                    live=False,
                )
            )

            # Generate a password reset link to be emailed to the user.
            password_reset_url = self.request.build_absolute_uri(
                get_set_password_url(student_user)
            )
            # Notify the user of the account.
            email_subject = _("Your Student account has been created")
            email_body = render_to_string(
                "account_management/admin/emails/notify_user_on_creation.txt",
                {
                    "finish_registration_url": password_reset_url,
                    "user": student_user,
                    "PASSWORD_RESET_TIMEOUT_DAYS": settings.PASSWORD_RESET_TIMEOUT_DAYS,
                },
            )

            send_mail(
                email_subject,
                email_body,
                "do-not-reply@rca.ac.uk",
                [student_user.email],
            )
            messages.success(
                self.request,
                f"The Student Page for {student_user} has been created."
                f"A Notification email has been sent to {student_user.email}",
            )

        return data
