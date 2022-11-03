from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from modelcluster.fields import ParentalKey
from wagtail.admin.mail import send_mail
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtailcaptcha.models import WagtailCaptchaEmailForm

from rca.utils.models import BasePage


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", related_name="form_fields")
    help_text = RichTextField(
        blank=True,
        features=("link",),
        verbose_name="help text",
    )


# Never cache form pages since they include CSRF tokens.
@method_decorator(never_cache, name="serve")
class FormPage(WagtailCaptchaEmailForm, BasePage):
    template = "patterns/pages/forms/form_page.html"
    landing_page_template = "patterns/pages/forms/form_page_landing.html"

    subpage_types = []

    introduction = RichTextField(blank=True)
    thank_you_text = RichTextField(
        blank=True,
        help_text="Text displayed to the user on successful submission of the form",
    )
    action_text = models.CharField(
        max_length=32, blank=True, help_text='Form action text. Defaults to "Submit"'
    )
    send_user_notification = models.BooleanField(
        blank=True,
        default=False,
        help_text="Tick to send the notification email to the user who submits "
        "the form, in addition to the addresses in 'To address'. "
        "The form must contain an email address field with the label "
        "'Email'.",
    )
    email_body_copy = models.TextField(
        blank=True,
        help_text="Enter the text to include in the body of the email.",
    )
    key_details = RichTextField(blank=True, features=["bold", "italic", "link", "h3"])

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("key_details"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("action_text"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
                FieldPanel("send_user_notification"),
                FieldPanel("email_body_copy"),
            ],
            "Email",
        ),
    ]

    key_details_panels = [FieldPanel("key_details")]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        return "Form"

    def process_form_submission(self, form):
        submission = super().process_form_submission(form)
        if self.send_user_notification:
            self.send_user_mail(form)
        return submission

    def send_user_mail(self, form):
        """Sends the email notification to the user who submitted the form.
        Depends on there being a form field labelled 'Email'"""
        address = form.cleaned_data.get("email")
        if address:
            send_mail(
                self.subject,
                self.render_email(form),
                [address],
                self.from_address,
            )

    def render_email(self, form):
        responses = super().render_email(form)

        content = [
            "Hi,",
            self.email_body_copy,
            "See below for the responses you submitted:",
            responses,
            "Kind regards,\n\nThe Royal College of Art team",
        ]

        content = "\n\n".join(content)
        return content
