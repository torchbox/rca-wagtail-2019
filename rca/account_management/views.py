from django.contrib.auth.models import Group
from django.views.generic import FormView

from rca.users.models import User

from .forms import StudentCreateForm


class CreateStudentFormView(FormView):

    template_name = "account_management/create.html"
    form_class = StudentCreateForm
    success_url = "/admin/student/create"  # TODO - better success template

    def form_valid(self, form):
        data = super().form_valid(form)
        student_group = Group.objects.get(name="Students")
        student_user = User.objects.create_user(
            username=form.cleaned_data["username"],
            password="123pass",
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        )
        student_user.groups.add(student_group)

        return data
