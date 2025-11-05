from django import forms
from wagtail.images.forms import BaseImageForm


class RCAImageForm(BaseImageForm):
    """Custom image form with rights confirmation checkbox."""

    rights_confirmed = forms.BooleanField(
        label="I confirm I have the rights to use the image I am uploading",
        help_text="Please confirm that you have the rights to use this image (owned, licensed, or free to use).",
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "checkbox-input"}),
    )
