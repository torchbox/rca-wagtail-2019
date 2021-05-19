from wagtail.users.forms import UserEditForm


class CustomUserEditForm(UserEditForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["readonly"] = "readonly"
        self.fields["username"].widget.attrs["disabled"] = "disabled"
