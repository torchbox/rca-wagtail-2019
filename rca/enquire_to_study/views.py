import json
import logging

import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from django_countries import countries
from django_countries.ioc_data import IOC_TO_ISO
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from wagtail.admin import messages

from .forms import EnquireToStudyForm
from .models import EnquireToStudySettings, EnquiryFormSubmission

logger = logging.getLogger(__name__)


class EnquireToStudyFormView(FormView):
    """Custom form with integrations to Mailchimp and QS

    On form submission, the post data is sent to different services depending
    on the 'country_of_residence' value. For the moment only QS is receiving
    post data, Mailchimp is incoming.

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
            "LevelOfStudy": "postgraduate",
            "Course": "307-graduate-diploma-art-and-design,127-ma-curating-contemporary-art-exhibitions-and-programming"
        }

    """

    form_class = EnquireToStudyForm
    success_url = "/enquire-to-study/thanks"
    template_name = "patterns/pages/enquire_to_study/enquire_form_page.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_mailchimp_interests_and_map_to_programmes(self, mailchimp, programmes):
        try:
            response = mailchimp.lists.list_interest_category_interests(
                settings.MAILCHIMP_LIST_ID,
                settings.MAILCHIMP_PROGRAMMES_INTEREST_CATEGORY_ID,
            )
            mailchimp_interest_ids = {}
            mapped_user_interests = {}
            try:
                for interest in response["interests"]:
                    mailchimp_interest_ids.update({interest["name"]: interest["id"]})
            except ValueError:
                return {}

            for program in programmes:
                if program.mailchimp_group_name:
                    try:
                        interest_id = mailchimp_interest_ids[
                            program.mailchimp_group_name
                        ]
                        mapped_user_interests.update({interest_id: True})
                    except KeyError:
                        logger.warning(
                            f"Mailchimp: Unable to map mailchimp_group_name for program page {program.id}"
                        )
                        pass
            return mapped_user_interests
        except ApiClientError as error:
            logger.exception(error.text)
            return {}

    def post_mailchimp(self, form_data):
        # see https://git.torchbox.com/nesta/nesta-wagtail/-/blob/master/nesta/mailchimp/api.py
        mailchimp = Client()
        mailchimp.set_config(
            {
                "api_key": settings.MAILCHIMP_API_KEY,
                "server": settings.MAILCHIMP_API_KEY.split("-")[-1],
            }
        )

        interests = {}
        if (
            form_data["programmes"]
            and settings.MAILCHIMP_PROGRAMMES_INTEREST_CATEGORY_ID
        ):
            interests = self.get_mailchimp_interests_and_map_to_programmes(
                mailchimp, form_data["programmes"]
            )
        elif not settings.MAILCHIMP_PROGRAMMES_INTEREST_CATEGORY_ID:
            logger.warning(
                "Mailchimp: Set MAILCHIMP_PROGRAMMES_INTEREST_CATEGORY_ID to assign users to groups"
            )

        country = dict(countries)[form_data["country_of_residence"]]

        member_info = {
            "merge_fields": {
                "FNAME": form_data["first_name"],
                "LNAME": form_data["last_name"],
                "PHONE": str(form_data["phone_number"]),
                "MMERGE6": form_data["start_date"].label,
                "MMERGE7": form_data["country_of_citizenship"],
                "ADDRESS": {
                    "addr1": "N/A",
                    "addr2": "N/A",
                    "city": form_data["city"],
                    "state": "N/A",
                    "zip": "N/A",
                    "country": country,
                },
            },
            "interests": interests,
            "email_address": form_data["email"],
            "status": "subscribed",
        }

        try:
            response = mailchimp.lists.add_list_member(
                settings.MAILCHIMP_LIST_ID, member_info
            )
            return response
        except ApiClientError as error:
            try:
                error_json = json.loads(error.text)
                if error_json["title"] and error_json["title"] == "Member Exists":
                    logger.info("Mailchimp: User tried to re-register to signup form")
                    return
            except ValueError:
                logger.warning("Mailchimp: failed to decode error message")
                return
            logger.exception(error.text)
            return

    def get_qs_data(self, query):
        return requests.get(
            f"{settings.QS_API_ENDPOINT}/{query}",
            auth=(settings.QS_API_USERNAME, settings.QS_API_PASSWORD),
        ).json()

    def post_qs(self, form_data):
        # Get data from QS student enquiry endpoint for matching up selected
        # programmes and programme types
        qs_level_studies = self.get_qs_data(query="levelofstudies")
        qs_courses = self.get_qs_data(query="courses")

        data = {
            "FirstName": form_data["first_name"],
            "LastName": form_data["last_name"],
            "EmailAddress": form_data["email"],
            "MobileNumber": f"{form_data['phone_number'].country_code}||{form_data['phone_number'].national_number}",
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

        # USE IOC format to send data, eg CA (Canada) Should be CAN
        for k, v in IOC_TO_ISO.items():
            if v == form_data["country_of_citizenship"]:
                data["CountryOfCitizenship"] = k
            if v == form_data["country_of_residence"]:
                data["CountryOfResidence"] = k

        selected_level_of_study_list = []
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
            level_of_study_code = next(
                (
                    level
                    for level in qs_level_studies
                    if level["code"] == programme.programme_type.qs_code
                ),
                None,
            )

            programme_type = form_data["programme_type"]
            level_of_study_code = next(
                (
                    level
                    for level in qs_level_studies
                    if level["code"] == programme_type.qs_code
                ),
                None,
            )
            if not level_of_study_code:
                raise ValueError(
                    f"{programme_type.display_name} not found in QS Level of study list"
                )

            level_of_study_code = level_of_study_code["code"]

            if level_of_study_code not in selected_level_of_study_list:
                selected_level_of_study_list.append(level_of_study_code)

        data["LevelOfStudy"] = ",".join(selected_level_of_study_list)
        data["Course"] = ",".join(selected_course_list)
        response = requests.post(
            f"{settings.QS_API_ENDPOINT}/studentEnquiries",
            json=data,
            auth=(settings.QS_API_USERNAME, settings.QS_API_PASSWORD),
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()

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
            settings.RCA_DNR_EMAIL,
            [user_email],
            fail_silently=False,
        )

    def form_valid(self, form):
        country_of_residence = form.cleaned_data["country_of_residence"]
        # If location UK/IRE
        # post_mailchimp
        # else
        # post_qs
        if country_of_residence in ["GB", "IE"]:
            self.post_mailchimp(form.cleaned_data)
        else:
            self.post_qs(form.cleaned_data)

        self.create_form_submission(form)
        if settings.RCA_DNR_EMAIL:
            self.send_user_email_notification(form)

        return super().form_valid(form)


class EnquireToStudyFormThanksView(TemplateView):
    template_name = "patterns/pages/enquire_to_study/enquire_form_thanks.html"


def delete(request):
    if not request.user.has_perm(
        "enquiry_form_submission:can_delete_enquiry_form_submission"
    ):
        raise PermissionDenied()

    from .wagtail_hooks import EnquiryFormSubmissionAdmin

    url_helper = EnquiryFormSubmissionAdmin().url_helper
    index_url = url_helper.get_action_url("index")

    instances = EnquiryFormSubmission.objects.all()
    count = len(instances)
    if request.method == "POST":
        for instance in instances:
            instance.delete()

        message_content = f"deleted {count} submissions"
        messages.success(request, message_content)

        return redirect(index_url)

    return TemplateResponse(
        request,
        "enquire_to_study/confirm_delete.html",
        {
            "count": count,
            "index_url": url_helper.get_action_url("index"),
            "submit_url": (reverse("enquiretostudy_delete")),
        },
    )
