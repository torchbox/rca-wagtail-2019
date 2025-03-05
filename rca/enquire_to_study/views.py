import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from django_countries.ioc_data import IOC_TO_ISO
from wagtail.admin import messages

from rca.utils.views import MetaTitleMixin

from .forms import EnquireToStudyForm
from .models import EnquireToStudySettings, EnquiryFormSubmission

logger = logging.getLogger(__name__)


class EnquireToStudyFormView(MetaTitleMixin, FormView):
    """Custom form with integrations to QS

    Keys can be seen here:
    https://qs-enrolment-solutions.screenstepslive.com/s/Help/m/enquiryapi/l/889815-application-endpoints#student-enquiry

    All form submissions will create a .models.EnquiryFormSubmission object.
    {
            "FirstName": "Kevin",
            "LastName": "Howbrook",
            "EmailAddress": "yourmail@mail.com",
            "MobileNumber": "44||1234567899",
            "subscribedToDirectEmails": True,
            "subscribedToDirectPhoneCalls": False,
            "subscribedToDirectSMS": False,
            "Source": "RCA Website Webform",
            "Intake": "jan-18",
            "Notes": "Enquiry reason: Reason 1",
            "tags": [{
                "TagType": "Source",
                "Tag": "rca_wf_xx_RCA Website Webform_xx_xx_xx-xx-xx"
            }],
            "consents": [{
                "Consent": True,
                "ConsentType": "is_read_data_protection_policy"
            }],
            "CountryOfCitizenship": "CAN",
            "CountryOfResidence": "CAN",
            "Address": "|||City||", // We don't record address lines so we only enter the city.
            "LevelOfStudy": "postgraduate",
            "Course": "307-graduate-diploma-art-and-design,127-ma-curating-contemporary-art-exhibitions-and-programming"
        }

    """

    meta_title = "Register your interest"
    form_class = EnquireToStudyForm
    success_url = "/register-your-interest/thanks"
    template_name = "patterns/pages/enquire_to_study/enquire_form_page.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_qs_data(self, query):
        return requests.get(
            f"{settings.QS_API_ENDPOINT}/{query}",
            auth=(settings.QS_API_USERNAME, settings.QS_API_PASSWORD),
        ).json()

    def post_qs(self, form_data):
        # Get data from QS student enquiry endpoint for matching up selected programmes
        qs_courses = self.get_qs_data(query="courses")

        data = {
            "FirstName": form_data["first_name"],
            "LastName": form_data["last_name"],
            "EmailAddress": form_data["email"],
            "MobileNumber": f"{form_data['phone_number'].country_code}||{form_data['phone_number'].national_number}",
            "Address": f"|||{form_data['city']}||",
            "subscribedToDirectEmails": form_data["is_notification_opt_in"],
            "subscribedToDirectPhoneCalls": False,
            "subscribedToDirectSMS": False,
            "Source": "RCA Website Webform",
            "Intake": form_data["start_date"].qs_code,
            "Notes": f"Enquiry reason: {form_data['enquiry_reason'].reason}",
            "tags": [
                {
                    "TagType": "Source",
                    "Tag": "rca_wf_xx_RCA Webform Submission_xx_xx_xx-xx-xx",
                }
            ],
            "consents": [
                {
                    "Consent": form_data["is_read_data_protection_policy"],
                    "ConsentType": "is_read_data_protection_policy",
                }
            ],
        }

        if enquiry_questions := form_data["enquiry_questions"]:
            data["Notes"] += f"; Enquiry questions: {enquiry_questions}"

        # USE IOC format to send data, eg CA (Canada) Should be CAN
        for k, v in IOC_TO_ISO.items():
            if v == form_data["country_of_citizenship"]:
                data["CountryOfCitizenship"] = k
            if v == form_data["country_of_residence"]:
                data["CountryOfResidence"] = k

        selected_course_list = []
        for programme in form_data["programmes"]:
            course_code = next(
                (
                    course
                    for course in qs_courses
                    if course["codeExternal"] == str(programme.qs_code)
                ),
                None,
            )
            if not course_code:
                raise ValueError(f"{programme.title} not found in QS course list")
            course_code = course_code["code"]

            if course_code not in selected_course_list:
                selected_course_list.append(course_code)

        data["Course"] = ",".join(selected_course_list)
        response = requests.post(
            f"{settings.QS_API_ENDPOINT}/studentEnquiries",
            json=data,
            auth=(settings.QS_API_USERNAME, settings.QS_API_PASSWORD),
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()

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
                email_content += f"{programme.title} {settings.WAGTAILADMIN_BASE_URL + programme.url} \n"

        user_email = form.cleaned_data["email"]
        send_mail(
            enquiry_form_settings.email_subject,
            email_content,
            settings.RCA_DNR_EMAIL,
            [user_email],
            fail_silently=False,
        )

    def send_internal_email_notification(self, form, enquiry_submission):
        # Prettify the form labels so we don't render them with `_` e.g. `first_name: John`.
        answers = {
            key.replace("_", " ").capitalize(): value
            for key, value in form.cleaned_data.items()
        }

        # Transform programmes into their string representation since it's going to be a QuerySet.
        answers["Programmes"] = ", ".join([str(p) for p in answers["Programmes"]])

        name = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"

        send_mail(
            f"Enquire to Study - {name}",
            render_to_string(
                "patterns/emails/enquire_to_study.txt",
                {"answers": answers, "enquiry_submission": enquiry_submission},
            ),
            settings.RCA_DNR_EMAIL,
            settings.ENQUIRE_TO_STUDY_DESTINATION_EMAILS,
            fail_silently=False,
        )

    def set_session_data(self, form_data, enquiry_submission):
        # Sets form data into session variable for analytics.
        self.request.session["enquiry_form_session_data"] = {
            "event": "form-submission",
            "formName": "Enquire to study form",
            "formId": "enquire_to_study_form",
            "countryResidence": form_data["country_of_residence"],
            "countryCitizen": form_data["country_of_citizenship"],
            "programme": [i.title for i in form_data["programmes"]],
            "starting": form_data["start_date"].label,
            "enquiryType": form_data["enquiry_reason"].reason,
            "newsletter": str(form_data["is_notification_opt_in"]),
            "submissionId": enquiry_submission.id,
        }

    def form_valid(self, form):
        country_of_residence = form.cleaned_data["country_of_residence"]

        if settings.QS_API_PASSWORD:
            self.post_qs(form.cleaned_data)

        enquiry_submission = form.save()

        # Set form session data to pass to analytics.
        self.set_session_data(form.cleaned_data, enquiry_submission)

        if settings.RCA_DNR_EMAIL:
            self.send_user_email_notification(form)

            if (
                settings.ENQUIRE_TO_STUDY_DESTINATION_EMAILS
                and country_of_residence in ["GB", "IE"]
                and form.cleaned_data["enquiry_questions"]
            ):
                self.send_internal_email_notification(form, enquiry_submission)

        return super().form_valid(form)


class EnquireToStudyFormThanksView(MetaTitleMixin, TemplateView):
    meta_title = "Thank you for your enquiry"
    template_name = "patterns/pages/enquire_to_study/enquire_form_thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # If there is a session variable containing form post data send this,
        # through to the thanks template.
        from django.utils.html import mark_safe

        if "enquiry_form_session_data" in self.request.session:
            context["enquiry_form_session_data"] = mark_safe(
                self.request.session["enquiry_form_session_data"]
            )
            # In case the page is refreshed, make sure we clear the session form data.
            del self.request.session["enquiry_form_session_data"]
        return context


def delete(request):
    if not request.user.has_perm(
        "enquiry_form_submission:can_delete_enquiry_form_submission"
    ):
        raise PermissionDenied()

    from .wagtail_hooks import EnquiryFormSubmissionAdmin

    url_helper = EnquiryFormSubmissionAdmin().url_helper
    index_url = url_helper.get_action_url("index")

    all_submissions = EnquiryFormSubmission.objects.all()

    time_threshold = timezone.now() - timedelta(days=7)
    instances = all_submissions.filter(Q(submission_date__lte=time_threshold))
    count_delete_submissions = len(instances)

    if request.method == "POST":
        instances.delete()

        message_content = f"deleted {count_delete_submissions} submissions"
        messages.success(request, message_content)

        return redirect(index_url)

    return TemplateResponse(
        request,
        "enquire_to_study/confirm_delete.html",
        {
            "count_all_submissions": len(all_submissions),
            "count_delete_submissions": count_delete_submissions,
            "index_url": url_helper.get_action_url("index"),
            "submit_url": (reverse("enquiretostudy_delete")),
        },
    )
