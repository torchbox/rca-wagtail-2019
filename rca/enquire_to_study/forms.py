import warnings
from django import forms


class EnquireToStudyForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your email *'}),
    )
