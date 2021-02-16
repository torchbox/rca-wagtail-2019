import warnings
from django import forms
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField


class EnquireToStudyForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your email *'}),
    )
    phone_number = PhoneNumberField()

    country_of_residence = CountryField().formfield()

    city = forms.CharField(max_length=255)

    is_citizen = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')],widget=forms.RadioSelect)

    PROGRAMME_CHOICES = [
        ('Pre-Masters', 'Pre-Masters'),
        ('Thought Masters', 'Thought Masters'),
        ('Postgraduate research', 'Postgraduate research')
    ]
    programmes = forms.MultipleChoiceField(choices=PROGRAMME_CHOICES, widget=forms.CheckboxSelectMultiple)

    COURSE_CHOICES = [
        ('Animation MA', 'Animation MA'),
        ('Architecture MA', 'Architecture MA'),
        ('Architecture MRes', 'Architecture MRes'),
        ('Ceramics & Glass MA', 'Ceramics & Glass MA'),
        ('City Design MA', 'City Design MA'),
        ('Communication Design MRes', 'Communication Design MRes'),
        ('Contemporary Art Practice MA', 'Contemporary Art Practice MA'),
        ('Curating Contemporary Art MA', 'Curating Contemporary Art MA'),
        ('Design MRes', 'Design MRes'),
        ('Design Products MA', 'Design Products MA'),
        ('Digital Direction MA', 'Digital Direction MA'),
        ('Environmental Architecture MA', 'Environmental Architecture MA'),
        ('Fashion MA', 'Fashion MA'),
        ('Fine Art & Humanities MRS', 'Fine Art & Humanities MRS'),
        ('Global Innovation Design MA/MSc', 'Global Innovation Design MA/MSc'),
        ('Healthcare & Design MRes', 'Healthcare & Design MRes'),
        ('History of Design MA (3 options)', 'History of Design MA (3 options)'),
        ('Information Experience Design MA(3 options)', 'Information Experience Design MA(3 options)'),
        ('Innovation Design Engineering MA/MSc', 'Innovation Design Engineering MA/MSc'),
        ('Intelligent Mobility MA', 'Intelligent Mobility MA'),
        ('Interior Design MA', 'Interior Design MA'),
        ('Jewellery & Metal MA', 'Jewellery & Metal MA'),
        ('Painting MA', 'Painting MA'),
        ('Photography MA', 'Photography MA'),
        ('Print MA', 'Print MA'),
        ('Sculpture MA', 'Sculpture MA'),
        ('Service Design MA', 'Service Design MA'),
        ('Textiles MA', 'Textiles MA'),
        ('Virtual Communication MA (3 options)', 'Virtual Communication MA (3 options)'),
        ('Writing MA', 'Writing MA'),
    ]
    courses = forms.MultipleChoiceField(choices=COURSE_CHOICES, widget=forms.CheckboxSelectMultiple)

    START_DATE_CHOICES = [
        ('2021/22', '2021/22'),
        ('2022', '2022 onwards')
    ]
    start_date = forms.ChoiceField(choices=START_DATE_CHOICES,widget=forms.RadioSelect)

    FUNDING_CHOICES = [
        ('Self Funded', 'Self Funded'),
        ('Bank Loan', 'Self Funded'),
        ('Business or Government funding', 'Self Funded'),
        ('Scholarships', 'Scholarships'),
        ('Other', 'Other'),
    ]
    funding = forms.MultipleChoiceField(choices=FUNDING_CHOICES,widget=forms.CheckboxSelectMultiple)

    INQUIRY_REASON_CHOICES = [
        ('Reason one', 'Reason one'),
        ('Reason two', 'Reason two'),
        ('Reason three', 'Reason three'),
        ('Reason four', 'Reason four'),
    ]
    inquiry_reason = forms.ChoiceField(choices=INQUIRY_REASON_CHOICES,widget=forms.RadioSelect)

    is_read_data_protection_policy = forms.BooleanField()
    is_notification_opt_in = forms.BooleanField()
