from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.search import index

from rca.utils.blocks import AccordionBlockWithTitle, GuideBlock
from rca.utils.models import BasePage, ContactFieldsMixin


class DonationFormPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/donate/donate.html"

    introduction = models.CharField(max_length=500, blank=True)
    body = StreamField(GuideBlock())
    further_information_title = models.CharField(blank=True, max_length=120)
    further_information = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name=_("Further information"),
    )
    form_id = models.CharField(
        max_length=255,
        help_text="The long number in brackets from the generated JavaScript snippet",
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
        index.SearchField("further_information"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("form_id"),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("further_information_title"),
                StreamFieldPanel("further_information"),
            ],
            heading=_("Further information"),
        ),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]

    def anchor_nav(self):
        """ Build list of data to be used as
        in-page navigation """
        items = []
        for i, block in enumerate(self.body):
            if block.block_type == "anchor_heading":
                items.append({"title": block.value, "link": f"#{slugify(block.value)}"})
        if self.form_id:
            items.append({"title": "Donate", "link": f"#bbox-root"})
        if self.further_information_title:
            items.append(
                {
                    "title": self.further_information_title,
                    "link": f"#{slugify(self.further_information_title)}",
                }
            )

        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["anchor_nav"] = self.anchor_nav()

        return context
