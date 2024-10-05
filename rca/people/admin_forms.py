from django import forms
from wagtail.admin.forms import WagtailAdminPageForm


class StudentPageAdminForm(WagtailAdminPageForm):
    """Validation for adding StudentPage"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = kwargs.get("for_user")

        if user:
            # Don't allow changing the user account or image collection once set as they are tied to permissions
            if (
                self.instance.student_user_image_collection
                and self.instance.student_user_account
            ):
                disabled_fields = [
                    "student_user_image_collection",
                    "student_user_account",
                ]
                for f in disabled_fields:
                    # Wrapped in a try except as when a student uses this form, these fields are hidden
                    # See rca.people.models.StudentPage.basic_content_panels and rca.people.utils.PerUserPageMixin
                    try:
                        self.fields[f].widget.attrs["disabled"] = True
                    except KeyError:
                        pass
            if self.instance.title and self.instance.slug and not user.is_student():
                readonly_fields = [
                    "title",
                    "slug",
                ]

                for f in readonly_fields:
                    self.fields[f].widget.attrs["readonly"] = True

            elif self.instance.title and self.instance.slug and user.is_student():
                hidden_fields = [
                    "title",
                    "slug",
                ]

                for f in hidden_fields:
                    self.fields[f].widget = forms.HiddenInput()
                    self.fields[f].class_name = "student-hidden"

    def clean(self):
        cleaned_data = super().clean()

        instance = getattr(self, "instance", None)
        # # As these fields are disabled once set, they need adding back into the post data
        if (
            instance
            and instance.student_user_image_collection
            and instance.student_user_account
        ):
            cleaned_data["student_user_image_collection"] = (
                instance.student_user_image_collection
            )
            cleaned_data["student_user_account"] = instance.student_user_account

        student_user_image_collection = cleaned_data.get(
            "student_user_image_collection", None
        )
        student_user_account = cleaned_data.get("student_user_account", None)

        if student_user_image_collection and not student_user_account:
            self.add_error(
                "student_user_account",
                "If you are adding an image collection to use on this profile, "
                "a student user account must be added.",
            )
        if student_user_account and not student_user_image_collection:
            self.add_error(
                "student_user_image_collection",
                "If you are adding a student user account so a student can access "
                "this page, an image collection must be added.",
            )

        return cleaned_data

    class Media:
        js = [
            "people/admin/js/student_edit_page.js",
        ]
