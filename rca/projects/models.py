from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import StreamField
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.home.models import HERO_COLOUR_CHOICES, LIGHT_TEXT_ON_DARK_IMAGE
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    GalleryBlock,
    LinkBlock,
    QuoteBlock,
)
from rca.utils.models import BasePage, RelatedStaffPageWithManualOptions


class ProjectPageSubjectPlacement(models.Model):
    page = ParentalKey("ProjectPage", related_name="subjects")
    subject = models.ForeignKey(
        "programmes.Subject", on_delete=models.CASCADE, related_name="projects"
    )
    panels = [FieldPanel("subject")]


class ProjectPageRelatedStaff(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey("projects.ProjectPage", related_name="related_staff")


class ProjectPageProjectLeadStaff(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey("projects.ProjectPage", related_name="project_lead")


class ProjectPage(BasePage):
    template = "patterns/pages/project/project_detail.html"

    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
    introduction = models.CharField(max_length=500, blank=True)
    introduction_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text=_("The text displayed next to the video play button"),
    )
    video = models.URLField(blank=True)
    body = StreamField(
        [
            ("quote_block", QuoteBlock()),
            (
                "rich_text_block",
                RichTextBlock(
                    features=["h2", "h3", "bold", "italic", "image", "ul", "ol", "link"]
                ),
            ),
            ("link_block", LinkBlock()),
        ],
        blank=True,
        verbose_name=_("General information about the project"),
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    funding = models.CharField(max_length=250, blank=True)
    specification_document = models.ForeignKey(
        "documents.CustomDocument",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    # School - blocked
    # Theme - taxonomy needed

    gallery = StreamField(
        [("slide", GalleryBlock())], blank=True, verbose_name=_("Gallery")
    )
    more_information = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name=_("More information"),
    )
    partners = StreamField(
        [("link", LinkBlock())], blank=True, verbose_name=_("Links to partners")
    )
    funders = StreamField(
        [("link", LinkBlock())], blank=True, verbose_name=_("Links to funders")
    )
    quote_carousel = StreamField(
        [("quote", QuoteBlock())], blank=True, verbose_name=_("Quote carousel")
    )
    contact_email = models.EmailField(blank=True)
    contact_url = models.URLField(blank=True)
    contact_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    contact_text = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [ImageChooserPanel("hero_image"), FieldPanel("hero_colour_option")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("introduction"),
                ImageChooserPanel("introduction_image"),
                FieldPanel("video"),
                FieldPanel("video_caption"),
            ],
            heading=_("Introduction"),
        ),
        StreamFieldPanel("body"),
        StreamFieldPanel("gallery"),
        StreamFieldPanel("more_information"),
        MultiFieldPanel(
            [
                InlinePanel("project_lead", label="Project team lead", max_num=1),
                InlinePanel("related_staff", label="Project team"),
            ],
            "Project team and staff",
        ),
        StreamFieldPanel("partners"),
        StreamFieldPanel("funders"),
        StreamFieldPanel("quote_carousel"),
        MultiFieldPanel(
            [
                ImageChooserPanel("contact_image"),
                FieldPanel("contact_text"),
                FieldPanel("contact_url"),
                FieldPanel("contact_email"),
            ],
            heading="Contact information",
        ),
    ]
    key_details_panels = [
        InlinePanel("subjects", label="RCA Experties"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("funding"),
        DocumentChooserPanel("specification_document"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def clean(self):
        errors = defaultdict(list)

        if self.end_date and self.end_date < self.start_date:
            errors["end_date"].append(
                _("Events involving time travel are not supported")
            )
        if not self.contact_email and not self.contact_url:
            errors["contact_url"].append(
                "Please add a target value for the contact us link"
            )
        if self.contact_email and self.contact_url:
            errors["contact_url"].append(
                "Only one of URL or an Email value is supported here"
            )

        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = "dark"
        if self.hero_colour_option == LIGHT_TEXT_ON_DARK_IMAGE:
            context["hero_colour"] = "light"
        subjects = []
        for i in self.subjects.all():
            subjects.append({"title": i.subject.title, "link": "TODO"})
        context["subjects"] = subjects
        context["project_lead"] = self.project_lead.select_related("image")
        context["related_staff"] = self.related_staff.select_related("image")

        return context


class ProjectPickerPage(BasePage):
    pass
