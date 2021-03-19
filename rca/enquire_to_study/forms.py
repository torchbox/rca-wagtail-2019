from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField

from rca.enquire_to_study.models import (
    EnquiryFormSubmission,
    EnquiryFormSubmissionProgrammesOrderable,
    EnquiryFormSubmissionProgrammeTypesOrderable,
    EnquiryReason,
    StartDate,
)
from rca.programmes.models import ProgrammePage, ProgrammeType


class EnquireToStudyForm(forms.Form):
    # Personal Details
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = PhoneNumberField()

    # Country of residence & citizenship
    country_of_residence = CountryField().formfield()
    city = forms.CharField(max_length=255)
    country_of_citizenship = CountryField().formfield()

    # Study details
    programme_types = forms.ModelMultipleChoiceField(
        queryset=ProgrammeType.objects.all().exclude(qs_code__exact=""),
        widget=forms.CheckboxSelectMultiple,
    )

    programmes = forms.ModelMultipleChoiceField(
        queryset=ProgrammePage.objects.filter(qs_code__isnull=False, live=True),
        widget=forms.CheckboxSelectMultiple,
    )

    start_date = forms.ModelChoiceField(
        queryset=StartDate.objects.filter(qs_code__isnull=False),
        widget=forms.RadioSelect,
    )

    # What's the enquiry about ?
    enquiry_reason = forms.ModelChoiceField(
        queryset=EnquiryReason.objects.all(), widget=forms.RadioSelect
    )

    # Legal & newsletter
    is_read_data_protection_policy = forms.BooleanField()
    is_notification_opt_in = forms.BooleanField(required=False)

    # Recaptcha
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def __init__(self, *args, **kwargs):
        super(EnquireToStudyForm, self).__init__(*args, **kwargs)
        # Placeholder
        self.fields["first_name"].widget.attrs["placeholder"] = "First name *"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last name *"
        self.fields["email"].widget.attrs["placeholder"] = "Email *"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Phone number *"
        self.fields["city"].widget.attrs["placeholder"] = "City or town of residence *"

        # Labels
        self.fields[
            "country_of_citizenship"
        ].label = "Which country are you a citizen of?"
        self.fields[
            "programme_types"
        ].label = "Type of programme(s) you're interested in"
        self.fields["programmes"].label = "The programme(s) you're interested in"
        self.fields["start_date"].label = "When do you plan to start your degree?"
        self.fields["enquiry_reason"].label = "What's your enquiry about?"
        self.fields["is_read_data_protection_policy"].label = (
            "I have read the data protection notice and agree for my data "
            "to be processed accordingly. "
        )
        self.fields["is_notification_opt_in"].label = (
            "From time to time we would like to notify you about events, news, "
            "opportunities, and services (including other courses) at RCA. "
            "Please tick this box to give your consent to be contacted in this way."
        )

        # Help Text
        self.fields[
            "phone_number"
        ].help_text = "Include your country code, for example +44"
        self.fields["programme_types"].help_text = "Select all that apply"
        self.fields["programmes"].help_text = "Select all that apply"
        self.fields[
            "enquiry_reason"
        ].help_text = "So we can ensure the correct department receives your message"
        self.fields["is_notification_opt_in"].help_text = (
            "We will not pass on your personal data to any third "
            "parties for marketing purposes."
        )

    def clean(self):
        cleaned_data = super().clean()
        if "programmes" in cleaned_data:
            programmes = cleaned_data["programmes"]
            if len(programmes) > 3:
                self.add_error(
                    "programmes",
                    forms.ValidationError("Please only select up to 3 programmes."),
                )
        return cleaned_data

    def save(self):
        data = self.cleaned_data.copy()
        programme_types = data.pop("programme_types")
        programmes = data.pop("programmes")
        data.pop("captcha")
        enquiry_submission = EnquiryFormSubmission.objects.create(**data)

        for programme_type in programme_types:
            EnquiryFormSubmissionProgrammeTypesOrderable.objects.create(
                enquiry_submission=enquiry_submission, programme_type=programme_type
            )

        for programme in programmes:
            EnquiryFormSubmissionProgrammesOrderable.objects.create(
                enquiry_submission=enquiry_submission, programme=programme
            )

        return enquiry_submission
