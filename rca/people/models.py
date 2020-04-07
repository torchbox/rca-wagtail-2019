from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.models import BasePage


class SocialMediaProfile(models.Model):
    person_page = ParentalKey("StaffPage", related_name="social_media_profile")
    site_titles = (("twitter", "Twitter"), ("linkedin", "LinkedIn"))
    site_urls = (
        ("twitter", "https://twitter.com/"),
        ("linkedin", "https://www.linkedin.com/in/"),
    )
    service = models.CharField(max_length=200, choices=site_titles)
    username = models.CharField(max_length=255)

    @property
    def profile_url(self):
        return dict(self.site_urls)[self.service] + self.username

    def clean(self):
        if self.service == "twitter" and self.username.startswith("@"):
            self.username = self.username[1:]


class StaffPagePhoneNumber(models.Model):
    page = ParentalKey("StaffPage", related_name="phone_numbers")
    phone_number = models.CharField(max_length=255)

    panels = [FieldPanel("phone_number")]


class StaffPage(BasePage):
    template = "patterns/pages/staff/staff_detail.html"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    job_title = models.CharField(max_length=255)
    introduction = models.TextField(blank=True)
    website = models.URLField(blank=True, max_length=255)
    email = models.EmailField(blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("first_name"), FieldPanel("last_name")], heading="Name"
        ),
        ImageChooserPanel("image"),
        FieldPanel("job_title"),
        InlinePanel("social_media_profile", label="Social accounts"),
        FieldPanel("website"),
        MultiFieldPanel(
            [FieldPanel("email"), InlinePanel("phone_numbers", label="Phone numbers")],
            heading="Contact information",
        ),
        FieldPanel("introduction"),
    ]
