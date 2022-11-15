from django import forms
from wagtail.admin.forms import WagtailAdminPageForm


class StudentPageAdminForm(WagtailAdminPageForm):
    """Validation for adding StudentPage"""

    def __init__(self, *args, **kwargs):
        super(StudentPageAdminForm, self).__init__(*args, **kwargs)

        user = kwargs.get("for_user")
        user_level = None
        """
        'is_active', 'is_anonymous', 'is_authenticated', 'is_staff', 'is_student', 'is_superuser'
        """
        if user.is_superuser:
            user_level = "superuser"
        elif user.is_student():
            user_level = "student"
        else:
            user_level = "locked"
        # print("superuser", user.is_superuser)
        # print("admin", user.is_student())
        # print(user.__dir__())
        # permission = None
        # if user.is_student():
        #     permission = "student"
        # elif user.is_admin():
        #     permission = "admin"
        # self.is_student = user.is_student()
        # print("is_student", self.is_student)

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

        if self.instance.title and self.instance.slug and not user_level == "student":
            readonly_fields = [
                "title",
                "slug",
            ]

            for f in readonly_fields:
                self.fields[f].widget.attrs["readonly"] = True

        elif self.instance.title and self.instance.slug and user_level == "student":
            hidden_fields = [
                "title",
                "slug",
            ]

            for tab in self.instance.edit_handler.children:
                for panel in tab.children:
                    if panel.__class__.__name__ == "FieldPanel":
                        if panel.field_name in hidden_fields:
                            panel.permission = "hidden"
            #         if hasattr(panel, "field_name") and panel.field_name in hidden_fields:
            #             panel.is_shown = False

            # if panel.heading in hidden_fields:
            #     panel.heading = None

            for f in hidden_fields:
                self.fields[f].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        instance = getattr(self, "instance", None)
        # # As these fields are disabled once set, they need adding back into the post data
        if (
            instance
            and instance.student_user_image_collection
            and instance.student_user_account
        ):
            cleaned_data[
                "student_user_image_collection"
            ] = instance.student_user_image_collection
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
