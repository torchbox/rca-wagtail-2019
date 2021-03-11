from django.conf import settings
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from .forms import EnquireToStudyForm
from .models import EnquireToStudySettings


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

    def send_user_email_notification(self, form):
        enquiry_form_settings = EnquireToStudySettings.for_request(self.request)
        if not enquiry_form_settings.email_submission_notifations:
            return
        email_content = enquiry_form_settings.email_content
        # add links to programmes for the response
        if "programmes" in form.cleaned_data:
            email_content += (
                "\n\nPlease see the following pages for more "
                "information about the courses you enquired about: \n"
            )
            for programme in form.cleaned_data["programmes"]:
                email_content += (
                    f"{programme.title} {settings.BASE_URL + programme.url} \n"
                )

        user_email = form.cleaned_data["email"]

        send_mail(
            enquiry_form_settings.email_subject,
            email_content,
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=False,
        )

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
        self.send_user_email_notification(form)

        return super().form_valid(form)


class EnquireToStudyFormThanksView(TemplateView):
    template_name = "patterns/pages/enquire_to_study/enquire_form_thanks.html"
