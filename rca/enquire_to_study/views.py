import json
from django.contrib import messages
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from .forms import EnquireToStudyForm
from wagtail.contrib.forms.models import FormSubmission


class EnquireToStudyFormView(FormView):
    """Cutsom form with integrations to Mailchimp and QS

    TODO:
        - The form will need to generate a submission object, so we can
            create a dataclip to send to google as a cv export.
        - Mailchimp Integration
        - QS Integration
    """

    form_class = EnquireToStudyForm
    success_url = '/enquire-to-study/thanks'
    template_name = 'enquire_to_study/enquire.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post_mailchimp(self):
        # see https://git.torchbox.com/nesta/nesta-wagtail/-/blob/master/nesta/mailchimp/api.py
        pass

    def post_qs(self):
        pass

    def create_form_submission(self):
        pass

    def form_valid(self, form):
        # TODO
        # If location UK/IRE
        # post_mailchimp
        # else
        # post_qs

        # create_form_submission

        return super().form_valid(form)


class EnquireToStudyFormThanksView(TemplateView):
    template_name = 'enquire_to_study/thanks.html'
