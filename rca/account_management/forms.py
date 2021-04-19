from django import forms
from django.contrib.auth.forms import UsernameField


class StudentCreateForm(forms.Form):
    # Personal Details
    username = UsernameField(
        widget=forms.TextInput(attrs={"autofocus": True}), required=True
    )
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
