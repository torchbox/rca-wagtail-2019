from django import forms

from rca.programmes.models import ProgrammePage
from rca.scholarships.models import ScholarshipFormSubmission, ScholarshipSnippet


class ScholarshipForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ScholarshipForm, self).__init__(*args, **kwargs)
        self.fields["programme"].label = "The programme(s) you're interested in"

    # Personal Details
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

    # Study details
    programme = forms.ModelChoiceField(
        queryset=ProgrammePage.objects.filter(
            qs_code__isnull=False, live=True
        ).order_by("title"),
        widget=forms.Select,
    )
    scholarships = forms.ModelMultipleChoiceField(
        queryset=ScholarshipSnippet.objects.all().order_by("title"),
        widget=forms.CheckboxSelectMultiple,
    )

    def save(self):
        data = self.cleaned_data.copy()
        # Pop these just so the spike can confirm the submission creations
        programme = data.pop("programme")
        scholarships = data.pop("scholarships")
        print("saving form")
        print(programme, scholarships)
        submission = ScholarshipFormSubmission.objects.create(**data)

        return submission
