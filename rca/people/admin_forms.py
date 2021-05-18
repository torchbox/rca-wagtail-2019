from wagtail.admin.forms import WagtailAdminPageForm


class StudentPageAdminForm(WagtailAdminPageForm):
    """Validation for adding StudentPage
    """

    def clean(self):
        cleaned_data = super().clean()

        student_user_image_collection = cleaned_data["student_user_image_collection"]
        student_user_account = cleaned_data["student_user_account"]

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
