from wagtail.users.forms import UserEditForm


class CustomUserEditForm(UserEditForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO This also needs to be removed from the POST data
        self.fields["username"].widget.attrs["readonly"] = True
