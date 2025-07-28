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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Move the rights_confirmed field to the end of the form
        if "rights_confirmed" in self.fields:
            rights_field = self.fields.pop("rights_confirmed")
            self.fields["rights_confirmed"] = rights_field
