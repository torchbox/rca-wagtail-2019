from collections import defaultdict

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.blocks import CharBlock, StructBlock, URLBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.utils.blocks import GalleryBlock
from rca.utils.models import BasePage, RelatedPage


class DegreeLevel(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class ProgrammeType(models.Model):
    display_name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)

    def __str__(self):
        return self.display_name


class ProgrammePageProgrammeType(models.Model):
    programme_type = models.ForeignKey("ProgrammeType", on_delete=models.CASCADE)
    page = ParentalKey("ProgrammePage", related_name="programme_types")

    panels = [FieldPanel("programme_type")]

    def __str__(self):
        return self.programme_type.display_name


class ProgrammePageRelatedProgramme(RelatedPage):
    source_page = ParentalKey("ProgrammePage", related_name="related_programmes")
    panels = [PageChooserPanel("page", "programmes.ProgrammePage")]


class ProgrammePageCareerOpportunities(Orderable):
    page = ParentalKey("ProgrammePage", related_name="career_opportunities")
    text = models.TextField(blank=True, null=True)
    panels = [FieldPanel("text")]


class ProgrammePage(BasePage):
    parent_page_types = ["ProgrammeIndexPage"]
    subpage_types = []
    template = "patterns/pages/programmes/programme_detail.html"

    # Comments resemble tabbed panels in the editor
    # Content
    degree_level = models.ForeignKey(
        DegreeLevel, on_delete=models.SET_NULL, blank=False, null=True, related_name="+"
    )
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_video = models.URLField(blank=True)
    hero_video_preview_image = models.ForeignKey(
        "images.CustomImage",
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
    related_content_title = models.CharField(
        blank=True,
        max_length=120,
        help_text="Large title displayed above the related content items, EG 'More opportunities to study at the RCA'",
    )

    # Key Details
    programme_details_credits = models.CharField(max_length=25, blank=True)
    programme_details_credits_suffix = models.CharField(
        max_length=1,
        choices=(("1", "credits"), ("2", "credits at FHEQ Level 6")),
        blank=True,
    )
    programme_details_time = models.CharField(max_length=25, blank=True)
    programme_details_time_suffix = models.CharField(
        max_length=1,
        choices=(
            ("1", "year programme"),
            ("2", "month programme"),
            ("3", "week programme"),
        ),
        blank=True,
    )
    programme_details_duration = models.CharField(
        max_length=1,
        choices=(
            ("1", "Full-time study"),
            ("2", "Full-time study with part-time option"),
            ("3", "Part-time study"),
        ),
        blank=True,
    )

    next_open_day_date = models.DateField(blank=True, null=True)
    link_to_open_days = models.URLField(blank=True)
    application_deadline = models.DateField(blank=True, null=True)
    application_deadline_options = models.CharField(
        max_length=1,
        choices=(
            ("1", "Applications closed. Please check back soon."),
            ("2", "Still accepting applications"),
        ),
        blank=True,
    )

    programme_specification = models.ForeignKey(
        "documents.CustomDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Programme Overview
    programme_description_title = models.CharField(max_length=50, blank=True)
    programme_description_subtitle = models.CharField(max_length=100, blank=True)
    programme_description_copy = RichTextField(blank=True)
    # Gallery
    programme_gallery_title = models.CharField(max_length=125, blank=True)
    programme_gallery = StreamField(
        [("slide", GalleryBlock())], blank=True, verbose_name="Programme gallery"
    )

    facilities_intro = models.CharField(blank=True, max_length=150)
    facilities_copy = models.TextField(blank=True, max_length=400)
    facilities_link = models.URLField(blank=True)
    facilities_link_text = models.CharField(blank=True, max_length=150)
    facilities_gallery = StreamField(
        [
            (
                "slide",
                StructBlock([("title", CharBlock()), ("image", ImageChooserBlock())]),
            )
        ],
        blank=True,
    )

    notable_alumni_text = models.TextField(blank=True)
    notable_alumni_links = StreamField(
        [
            (
                "Link_to_person",
                StructBlock(
                    [("name", CharBlock()), ("link", URLBlock(required=False))],
                    icon="link",
                ),
            )
        ],
        blank=True,
    )

    contact_title = models.CharField(max_length=125, default="Contact us")
    contact_text = models.TextField(blank=True)
    contact_link_url = models.URLField(blank=True)
    contact_link_text = models.CharField(blank=True, max_length=125)
    contact_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Staff (api fetch)
    # Alumni Stories Carousel (api fetch)
    # Related Content (news and events)

    content_panels = BasePage.content_panels + [
        # Taxonomy, relationships etc
        FieldPanel("degree_level"),
        InlinePanel(
            "programme_types",
            label="Programme Type",
            help_text="Used to show content related to this programme page",
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel("hero_image"),
                FieldPanel("hero_video"),
                ImageChooserPanel("hero_video_preview_image"),
                FieldPanel("hero_colour_option"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("related_content_title"),
                InlinePanel("related_programmes", label="Related programmes"),
            ],
            heading="Related content",
        ),
    ]
    key_details_panel = [
        MultiFieldPanel(
            [
                FieldPanel("programme_details_credits"),
                FieldPanel("programme_details_credits_suffix"),
                FieldPanel("programme_details_time"),
                FieldPanel("programme_details_time_suffix"),
                FieldPanel("programme_details_duration"),
            ],
            heading="Details",
        ),
        FieldPanel("next_open_day_date"),
        FieldPanel("link_to_open_days"),
        FieldPanel("application_deadline"),
        FieldPanel(
            "application_deadline_options",
            help_text="Optionally display information about the deadline",
        ),
        InlinePanel("career_opportunities", label="Career Opportunities"),
        DocumentChooserPanel("programme_specification"),
    ]
    programme_overview_pannels = [
        MultiFieldPanel(
            [
                FieldPanel("programme_description_title"),
                FieldPanel("programme_description_subtitle"),
                FieldPanel("programme_description_copy"),
            ],
            heading="Programme Description",
        ),
        MultiFieldPanel(
            [
                FieldPanel("programme_gallery_title"),
                StreamFieldPanel("programme_gallery"),
            ],
            heading="Programme gallery",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facilities_intro"),
                FieldPanel("facilities_copy"),
                FieldPanel("facilities_link"),
                FieldPanel("facilities_link_text"),
                StreamFieldPanel("facilities_gallery"),
            ],
            heading="Facilities",
        ),
        MultiFieldPanel(
            [
                FieldPanel(
                    "notable_alumni_text", widget=forms.Textarea(attrs={"rows": "4"})
                ),
                StreamFieldPanel("notable_alumni_links"),
            ],
            heading="Alumni",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_title"),
                FieldPanel("contact_text", widget=forms.Textarea(attrs={"rows": "4"})),
                FieldPanel("contact_link_url"),
                FieldPanel("contact_link_text"),
                ImageChooserPanel("contact_image"),
            ],
            heading="Contact information",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panel, heading="Key details"),
            ObjectList(programme_overview_pannels, heading="Programme Overview"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    search_fields = BasePage.search_fields + []

    def clean(self):
        errors = defaultdict(list)
        # if self.hero_video and self.hero_image:
        #     errors["hero_image"].append("Please select a video OR an image, both are not needed.")
        if self.hero_video and not self.hero_video_preview_image:
            errors["hero_video_preview_image"].append(
                "Please add a preview image for the video."
            )
        if self.programme_details_credits and not self.programme_details_credits_suffix:
            errors["programme_details_credits_suffix"].append("Please add a suffix")
        if self.programme_details_credits_suffix and not self.programme_details_credits:
            errors["programme_details_credits"].append("Please add a credit value")
        if self.programme_details_time and not self.programme_details_time_suffix:
            errors["programme_details_time_suffix"].append("Please add a suffix")
        if self.programme_details_time_suffix and not self.programme_details_time:
            errors["programme_details_time"].append("Please add a time value")

        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = "dark"
        if self.hero_colour_option == "1":
            context["hero_colour"] = "light"

        context["related_sections"] = [
            {
                "title": "Related programmes",
                "related_items": [
                    rel.page.specific
                    for rel in self.related_programmes.select_related("page")
                ],
            }
        ]
        # Set the page tab titles
        context["tabs"] = [
            {"title": "Programme Overview"},
            {"title": "Curriculum"},
            {"title": "Requirements"},
            {"title": "Fees and funding"},
            {"title": "Apply"},
        ]

        return context


class ProgrammeIndexPage(BasePage):
    subpage_types = ["ProgrammePage"]
    template = "patterns/pages/programmes/programme_index.html"

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [FieldPanel("introduction")]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        subpages = self.get_children().live()
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get("page")
        paginator = Paginator(subpages, per_page)

        try:
            subpages = paginator.page(page_number)
        except PageNotAnInteger:
            subpages = paginator.page(1)
        except EmptyPage:
            subpages = paginator.page(paginator.num_pages)

        context["subpages"] = subpages

        return context
