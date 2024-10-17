from django import forms
from wagtail.users.forms import UserEditForm


class CustomUserEditForm(UserEditForm):

    class Meta(UserEditForm.Meta):
        widgets = {
            "username": forms.TextInput(attrs={"readonly": True}),
        }
