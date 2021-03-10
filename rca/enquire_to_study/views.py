from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from .forms import EnquireToStudyForm


class EnquireToStudyFormView(FormView):
    """Cutsom form with integrations to Mailchimp and QS
    """

    form_class = EnquireToStudyForm
    success_url = "/enquire-to-study/thanks"
    template_name = "patterns/pages/enquire_to_study/enquire_form_page.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post_mailchimp(self):
        # see https://git.torchbox.com/nesta/nesta-wagtail/-/blob/master/nesta/mailchimp/api.py
        pass

    def post_qs(self, form_data):
        pass

    def create_form_submission(self, form):
        form.save()

    def form_valid(self, form):
        country_of_residence = form.cleaned_data["country_of_residence"]
        # If location UK/IRE
        # post_mailchimp
        # else
        # post_qs
        if country_of_residence == "GB" or country_of_residence == "IE":
            self.post_mailchimp()
        else:
            self.post_qs(form.cleaned_data)

        self.create_form_submission(form)

        return super().form_valid(form)


class EnquireToStudyFormThanksView(TemplateView):
    template_name = "patterns/pages/enquire_to_study/enquire_form_thanks.html"
