from collections import defaultdict

from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.forms import WagtailAdminPageForm


class StudentPageAdminForm(WagtailAdminPageForm):
    """Validation for adding StudentPage
    """

    def clean(self):
        cleaned_data = super().clean()
        errors = defaultdict(list)
        StudentPage = apps.get_model("people.StudentPage")

        student_user_account = cleaned_data.get("student_user_account")

        if student_user_account:
            try:
                StudentPage.objects.get(student_user_account=student_user_account)
            except StudentPage.DoesNotExist:
                pass
            else:
                errors["student_user_account"].append(
                    _("The Student you have selected already has a user account")
                )

        if errors:
            raise ValidationError(errors)

        return cleaned_data
