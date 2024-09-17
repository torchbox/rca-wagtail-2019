from django import forms
from django.utils.safestring import mark_safe
from django_countries.fields import CountryField
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from phonenumber_field.formfields import PhoneNumberField

from rca.enquire_to_study.models import (
    EnquiryFormSubmission,
    EnquiryFormSubmissionProgrammesOrderable,
    EnquiryReason,
    StartDate,
)
from rca.programmes.models import ProgrammePage


class EnquireToStudyForm(forms.Form):
    # Personal Details
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = PhoneNumberField()

    # Country of residence & citizenship
    country_of_residence = CountryField().formfield()
    city = forms.CharField(max_length=20, label="City or town of residence")
    country_of_citizenship = CountryField().formfield()

    # Study details
    programmes = forms.ModelMultipleChoiceField(
        queryset=ProgrammePage.objects.filter(
            qs_code__isnull=False, live=True
        ).order_by("title"),
        widget=forms.CheckboxSelectMultiple,
    )

    start_date = forms.ModelChoiceField(
        queryset=StartDate.objects.filter(qs_code__isnull=False),
        widget=forms.RadioSelect,
        empty_label=None,
    )

    # What's the enquiry about ?
    enquiry_reason = forms.ModelChoiceField(
        queryset=EnquiryReason.objects.all(), widget=forms.RadioSelect, empty_label=None
    )

    enquiry_questions = forms.CharField(
        label="Your questions (optional)",
        help_text="If you have a specific enquiry or question, please include it here.",
        required=False,
        widget=forms.Textarea,
    )

    # Legal & newsletter
    is_read_data_protection_policy = forms.BooleanField()
    is_notification_opt_in = forms.BooleanField(required=False)

    # Recaptcha
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Placeholder

        # Set initial values
        self.fields["country_of_residence"].initial = ("GB", "United Kingdon")
        self.fields["country_of_citizenship"].initial = ("GB", "United Kingdom")

        # Labels
        self.fields["country_of_citizenship"].label = (
            "Which country are you a citizen of?"
        )
        self.fields["programmes"].label = (
            "The preferred programme(s) you're interested in"
        )
        self.fields["start_date"].label = "When do you plan to start your degree?"
        self.fields["enquiry_reason"].label = "What's your enquiry about?"
        self.fields["is_read_data_protection_policy"].label = mark_safe(
            '<span class="rich-text form-item__rich-text">I acknowledge the RCA’s <a class="link link--link" '
            'href="https://www.rca.ac.uk/data-protection-privacy-cookies/" '
            'target="_blank">Enquirer Privacy Notice</a> and understand that my personal '
            "data will be processed in accordance with this notice.</span>"
        )
        self.fields["is_notification_opt_in"].label = mark_safe(
            "<span class='rich-text form-item__rich-text'>"
            "From time to time we would like to notify you about events, news, "
            "opportunities, and services (including other courses) at RCA. "
            "Please tick this box to give your consent to be contacted in this way."
            " To withdraw consent, email <a class='link link--link' href='mailto:dpo@rca.ac.uk'>"
            "dpo@rca.ac.uk</a> or send your request to "
            "our Data Protection Officer at the following address: The Royal "
            "College of Art, Kensington Gore, London SW7 2EU."
            "</span>"
        )

        # Disable browser autocomplete for city field
        self.fields["city"].widget.attrs.update({"autocomplete": "off"})

        # Help Text
        self.fields["phone_number"].help_text = (
            "You must include your country code, e.g. +442075904444"
        )
        self.fields["programmes"].help_text = "Select up to 2 programmes"
        self.fields["enquiry_reason"].help_text = (
            "This will help ensure the correct department receives your enquiry"
        )
        self.fields["city"].help_text = "e.g. London, Mumbai, New York"

    def clean(self):
        cleaned_data = super().clean()
        if "programmes" in cleaned_data:
            programmes = cleaned_data["programmes"]
            if len(programmes) > 2:
                self.add_error(
                    "programmes",
                    forms.ValidationError("Please only select up to 2 programmes."),
                )
        return cleaned_data

    def save(self):
        data = self.cleaned_data.copy()
        programmes = data.pop("programmes")
        data.pop("captcha")
        enquiry_submission = EnquiryFormSubmission.objects.create(**data)

        for programme in programmes:
            EnquiryFormSubmissionProgrammesOrderable.objects.create(
                enquiry_submission=enquiry_submission, programme=programme
            )

        return enquiry_submission
