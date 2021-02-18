import warnings

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField

from rca.enquire_to_study.models import Submission, Funding, SubmissionFundingsOrderable, InquiryReason, StartDate
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
    is_citizen = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.RadioSelect)

    # Study details
    programme_types = forms.ModelMultipleChoiceField(queryset=ProgrammeType.objects.all(),
                                                     widget=forms.CheckboxSelectMultiple)

    programmes = forms.ModelMultipleChoiceField(queryset=ProgrammePage.objects.live(),
                                                widget=forms.CheckboxSelectMultiple)

    start_date = forms.ModelChoiceField(queryset=StartDate.objects.all(), widget=forms.RadioSelect)

    funding = forms.ModelMultipleChoiceField(queryset=Funding.objects.all(), widget=forms.CheckboxSelectMultiple)

    # What's the enquiry about ?
    inquiry_reason = forms.ModelChoiceField(queryset=InquiryReason.objects.all(), widget=forms.RadioSelect)

    # Legal & newsletter
    is_read_data_protection_policy = forms.BooleanField()
    is_notification_opt_in = forms.BooleanField(required=False)

    # Recaptcha
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def __init__(self, *args, **kwargs):
        super(EnquireToStudyForm, self).__init__(*args, **kwargs)
        # Placeholder
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name *'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name *'
        self.fields['email'].widget.attrs['placeholder'] = 'Email *'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone number *'
        self.fields['city'].widget.attrs['placeholder'] = 'City or town of residence *'

        # Labels
        self.fields['is_citizen'].label = 'Are you also a citizen in this country?'
        self.fields['programme_types'].label = 'Type of programme(s) you\'re interested in'
        self.fields['programmes'].label = 'The programme(s) you\'re interested in'
        self.fields['start_date'].label = 'When do you plan to start your degree?'
        self.fields['funding'].label = 'How do you plan on funding your study?'
        self.fields['inquiry_reason'].label = 'What\'s your enquiry about?'

        # Help Text
        self.fields['phone_number'].help_text = 'Include your country code, for example +44'
        self.fields['programme_types'].help_text = 'Select all that apply'
        self.fields['programmes'].help_text = 'Select all that apply'
        self.fields['funding'].help_text = 'Select all that apply'
        self.fields['inquiry_reason'].help_text = 'So we can ensure the correct department receives your message'

    def save(self):
        data = self.cleaned_data.copy()

        programmes = data.pop("programmes")
        courses = data.pop("courses")
        fundings = data.pop("funding")
        data["inquiry_reason"] = InquiryReason.objects.get_or_create(reason=data.pop("inquiry_reason"))[0]
        data.pop("captcha")

        submission = Submission.objects.create(**data)

        for funding in fundings:
            funding = Funding.objects.get_or_create(funding=funding)[0]
            SubmissionFundingsOrderable.objects.create(submission=submission, funding=funding)
