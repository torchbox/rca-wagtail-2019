import logging

from django.contrib.auth.models import Group
from django.views.generic import FormView

from rca.people.models import StudentIndexPage, StudentPage
from rca.users.models import User

from .forms import StudentCreateForm

logger = logging.getLogger(__name__)


class CreateStudentFormView(FormView):

    template_name = "account_management/create.html"
    form_class = StudentCreateForm
    success_url = "/admin/student/create"  # TODO - better success template

    def form_valid(self, form):
        data = super().form_valid(form)
        # Create the student account
        student_group = Group.objects.get(name="Students")
        # TODO This is throwing an Integrity error with duplicate names,
        # we should add an error to the form and return it.
        student_user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        )
        student_user.set_unusable_password()
        # Add the student group
        student_user.groups.add(student_group)

        if not form.cleaned_data["create_student_page"]:
            return data

        # Is there a student index page we can create a student page under?
        student_index = StudentIndexPage.objects.first()
        if not student_index:
            logger.info(
                "There is not StudentIndex page to create a StudentPage under, "
                f"so one has not been created for user: {student_user}"
            )
            return data

        # Does a student page already exist for this user?
        student_page = StudentPage.objects.filter(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        ).exists()

        if student_page:
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
        return data
