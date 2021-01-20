from django import template

from rca.enquire_to_study.forms import EnquireToStudyForm


register = template.Library()


@register.simple_tag
def enquire_to_study_form():
    return EnquireToStudyForm()
