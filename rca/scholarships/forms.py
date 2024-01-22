from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from rca.programmes.models import ProgrammePage

from .models import (
    Scholarship,
    ScholarshipEnquiryFormSubmission,
    ScholarshipEnquiryFormSubmissionScholarshipOrderable,
)


class ScholarshipSubmissionForm(forms.ModelForm):
    scholarships = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label=_("Which scholarship(s) you're interested in"),
        help_text=_("Select all that apply"),
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def __init__(self, *args, **kwargs):
        programme = kwargs.pop("programme", None)
        super().__init__(*args, **kwargs)
        scholarships = Scholarship.objects.all()
        self.fields["programme"].queryset = ProgrammePage.objects.live().order_by(
            "title"
        )
        if programme:
            self.fields["programme"].initial = programme
            scholarships = scholarships.filter(eligable_programmes=programme)
        self.fields["scholarships"].queryset = scholarships
        self.fields["is_read_data_protection_policy"].required = True

    def save(self, commit=True):
        submission = super().save(commit=False)
        scholarships = self.cleaned_data.get("scholarships", [])
        for scholarship in scholarships:
            submission.scholarship_submission_scholarships.add(
                ScholarshipEnquiryFormSubmissionScholarshipOrderable(
                    scholarship_submission=submission, scholarship=scholarship
                )
            )
        submission.save()
        self.save_m2m()
        return submission

    class Meta:
        model = ScholarshipEnquiryFormSubmission
        fields = (
            "first_name",
            "last_name",
            "email",
            "rca_id_number",
            "programme",
            "scholarships",
            "eligibility_criteria",
            "is_read_data_protection_policy",
            "is_notification_opt_in",
            "captcha",
        )
        help_texts = {
            "eligibility_criteria": _("Select all that apply"),
            "rca_id_number": _("You can find this on your offer letter"),
            "is_notification_opt_in": _(
                _(
                    "We will not pass on your personal data to any third parties for marketing purposes."
                )
            ),
        }
        labels = {
            "eligibility_criteria": _("Scholarship eligibility"),
            "programme": _("Which programme is your offer for?"),
            "is_read_data_protection_policy": _(
                mark_safe(
                    '<span class="rich-text form-item__rich-text">I have read the <a class="link link--link" '
                    'href="https://www.rca.ac.uk/data-protection-privacy-cookies/" '
                    'target="_blank">data protection notice</a> '
                    "and agree for my data to be processed accordingly</span>"
                )
            ),
            "is_notification_opt_in": _(
                _(
                    "From time to time we would like to notify you by email about events, news, "
                    "opportunities, and services (including other courses) at RCA. Please tick this "
                    "box to give your consent to be contacted in this way"
                )
            ),
            "rca_id_number": "RCA ID number",
        }
        widgets = {
            "eligibility_criteria": forms.CheckboxSelectMultiple,
        }
