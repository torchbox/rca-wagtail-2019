from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.models import BasePage


class HomePage(BasePage):
    template = "patterns/pages/home/home_page.html"

    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.CharField(
        max_length=1,
        choices=(
            ("1", "Light text on a dark image"),
            ("2", "Dark text on a light image"),
        ),
    )
    hero_cta_url = models.URLField(blank=True)
    hero_cta_text = models.CharField(max_length=125, blank=True)
    hero_cta_sub_text = models.CharField(max_length=125, blank=True)

    strapline = models.CharField(max_length=125)
    strapline_cta_url = models.URLField(blank=True)
    strapline_cta_text = models.CharField(max_length=125, blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                ImageChooserPanel("hero_image"),
                FieldPanel("hero_colour_option"),
                FieldPanel("hero_cta_url"),
                FieldPanel("hero_cta_text"),
                FieldPanel("hero_cta_sub_text"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("strapline"),
                FieldPanel("strapline_cta_url"),
                FieldPanel("strapline_cta_text"),
            ],
            heading="Strapline",
        ),
    ]

    def clean(self):
        errors = defaultdict(list)
        if self.hero_cta_url and not self.hero_cta_text:
            errors["hero_cta_text"].append(
                "Please add the text to be displayed as a link"
            )
        if self.hero_cta_text and not self.hero_cta_url:
            errors["hero_cta_url"].append("Please add a URL value")
        if self.strapline_cta_url and not self.strapline_cta_text:
            errors["hero_cta_text"].append(
                "Please add the text to be displayed as a link"
            )
        if self.strapline_cta_text and not self.strapline_cta_url:
            errors["hero_cta_url"].append("Please add a URL value")

        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = "dark"
        if self.hero_colour_option == "1":
            context["hero_colour"] = "light"

        return context
