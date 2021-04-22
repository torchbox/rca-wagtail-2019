from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.forms import WagtailAdminPageForm


class StudentPageAdminForm(WagtailAdminPageForm):
    """Validation for adding StudentPage
    """

    def __init__(self, *args, **kwargs):
        print(args)
        print(kwargs)
        super(StudentPageAdminForm, self).__init__(*args, **kwargs)
        # TODO work in request.user.group IS/HAS Student and lock fields
        # readonly_fields = [
        #     "first_name",
        #     "last_name",
        # ]
        # for f in readonly_fields:
        #     self.fields[f].widget.attrs["readonly"] = "readonly"
        #     self.fields[f].widget.attrs["disabled"] = "disabled"

    def clean(self):
        cleaned_data = super().clean()
        # Avoid circular import
        StudentPage = apps.get_model("people.StudentPage")

        student_user_account = cleaned_data.get("student_user_account")

        if (
            student_user_account
            and StudentPage.objects.filter(
                student_user_account=student_user_account
            ).exists()
        ):
            raise ValidationError(
                {
                    "student_user_account": _(
                        "The Student you have selected already has a user account"
                    )
                }
            )
        return cleaned_data
