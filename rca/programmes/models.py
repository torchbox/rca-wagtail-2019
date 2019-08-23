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
from wagtail.embeds import embeds
from wagtail.embeds.exceptions import EmbedException
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.home.models import HERO_COLOUR_CHOICES, LIGHT_TEXT_ON_DARK_IMAGE
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    FeeBlock,
    GalleryBlock,
    InfoBlock,
    StepBlock,
)
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


class ProgrammePageFeeItem(Orderable):
    page = ParentalKey("ProgrammePage", related_name="fee_items")
    title = models.CharField(
        max_length=120,
        help_text="The title for the information, e.g 'Fees for new students ",
    )
    introduction = models.CharField(
        max_length=250, help_text="Extra information about the fee items"
    )
    row = StreamField([("row", FeeBlock())], blank=True)
    panels = [FieldPanel("title"), FieldPanel("introduction"), StreamFieldPanel("row")]

    def __str__(self):
        return self.title


class ProgrammePageRelatedProgramme(RelatedPage):
    source_page = ParentalKey("ProgrammePage", related_name="related_programmes")
    panels = [PageChooserPanel("page", "programmes.ProgrammePage")]


class ProgrammePageCareerOpportunities(Orderable):
    page = ParentalKey("ProgrammePage", related_name="career_opportunities")
    text = models.TextField(blank=True, null=True)
    panels = [FieldPanel("text")]


class ProgramPageRelatedStaff(Orderable):
    # In a future phase, this will become a related page
    source_page = ParentalKey("ProgrammePage", related_name="related_staff")
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    name = models.CharField(max_length=125)
    role = models.CharField(max_length=125, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)
    link_text = models.CharField(max_length=125, blank=True)
    panels = [
        ImageChooserPanel("image"),
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("description"),
        FieldPanel("link"),
        FieldPanel("link_text"),
    ]

    def __str__(self):
        return self.name


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
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
    related_content_title = models.CharField(
        blank=True,
        max_length=120,
        help_text="Large title displayed above the related content items, "
        "e.g. 'More opportunities to study at the RCA'",
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

    programme_gallery_title = models.CharField(max_length=125, blank=True)
    programme_gallery = StreamField(
        [("slide", GalleryBlock())], blank=True, verbose_name="Programme gallery"
    )

    # Staff
    staff_link = models.URLField(blank=True)
    staff_link_text = models.CharField(
        max_length=125, blank=True, help_text="E.g. 'See all programme staff'"
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

    # TODO
    # Alumni Stories Carousel (api fetch)
    # Related Content (news and events api fetch)

    # Programme Curriculumm
    curriculum_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    curriculum_subtitle = models.CharField(blank=True, max_length=100)
    curriculum_video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text="The text dipsplayed next to the video play button",
    )
    curriculum_video = models.URLField(blank=True)
    curriculum_text = models.TextField(blank=True, max_length=250)

    # Pathways
    pathways_summary = models.CharField(blank=True, max_length=150)
    # The summary can't be part of the block because it needs to be rendered in multiple places
    # in the template so it's best to keep it separate
    pathways_information = models.TextField(blank=True)
    pathway_blocks = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name="Accordion blocks",
    )
    what_you_will_cover_blocks = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name="Accordion blocks",
    )

    # Requirements
    requirements_subtitle = models.CharField(blank=True, max_length=100)
    requirements_text = models.CharField(blank=True, max_length=250)

    requirements_blocks = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name="Accordion blocks",
    )

    # fees
    # Scholarships
    scholarships_title = models.CharField(max_length=120)
    scholarships_information = models.CharField(max_length=250)
    scholarship_accordion_items = StreamField(
        [("accodrion", AccordionBlockWithTitle())], blank=True
    )
    scholarship_information_blocks = StreamField(
        [("information_block", InfoBlock())], blank=True
    )
    # More information
    more_information_blocks = StreamField(
        [("information_block", InfoBlock())], blank=True
    )

    # Apply
    apply_title = models.CharField(max_length=125, default="Start your application")
    apply_image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    apply_image_title = models.CharField(max_length=125, blank=True)
    apply_image_sub_title = models.CharField(max_length=250, blank=True)
    steps = StreamField([("step", StepBlock())], blank=True)
    apply_cta_link = models.URLField()
    apply_cta_text = models.CharField(max_length=125)

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
    key_details_panels = [
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
                InlinePanel("related_staff", max_num=2),
                FieldPanel("staff_link"),
                FieldPanel("staff_link_text"),
            ],
            heading="Staff",
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
    programme_curriculum_pannels = [
        MultiFieldPanel(
            [
                ImageChooserPanel("curriculum_image"),
                FieldPanel("curriculum_subtitle"),
                FieldPanel("curriculum_video"),
                FieldPanel("curriculum_video_caption"),
                FieldPanel("curriculum_text"),
            ],
            heading="Curriculum introduction",
        ),
        MultiFieldPanel(
            [
                FieldPanel("pathways_summary"),
                FieldPanel(
                    "pathways_information", widget=forms.Textarea(attrs={"rows": "4"})
                ),
                StreamFieldPanel("pathway_blocks"),
            ],
            heading="Pathways",
        ),
        MultiFieldPanel(
            [StreamFieldPanel("what_you_will_cover_blocks")],
            heading="What you'll cover",
        ),
    ]

    programme_requirements_pannels = [
        FieldPanel("requirements_subtitle"),
        FieldPanel("requirements_text", widget=forms.Textarea(attrs={"rows": "4"})),
        StreamFieldPanel("requirements_blocks"),
    ]
    programme_fees_and_funding_panels = [
        MultiFieldPanel(
            [InlinePanel("fee_items", label="Fee items")], heading="For this program"
        ),
        MultiFieldPanel(
            [
                FieldPanel("scholarships_title"),
                FieldPanel("scholarships_information"),
                StreamFieldPanel("scholarship_accordion_items"),
                StreamFieldPanel("scholarship_information_blocks"),
            ],
            heading="Scholarships",
        ),
        MultiFieldPanel(
            [StreamFieldPanel("more_information_blocks")], heading="More information"
        ),
    ]
    programme_apply_pannels = [
        MultiFieldPanel(
            [
                FieldPanel("apply_title"),
                ImageChooserPanel("apply_image"),
                FieldPanel("apply_image_title"),
                FieldPanel("apply_image_sub_title"),
            ],
            heading="Introduction image",
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel("steps"),
                FieldPanel("apply_cta_link"),
                FieldPanel("apply_cta_text"),
            ],
            heading="Before you begin",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(programme_overview_pannels, heading="Overview"),
            ObjectList(programme_curriculum_pannels, heading="Curriculum"),
            ObjectList(programme_requirements_pannels, heading="Requirements"),
            ObjectList(programme_fees_and_funding_panels, heading="Fees"),
            ObjectList(programme_apply_pannels, heading="Apply"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    search_fields = BasePage.search_fields + []

    def clean(self):
        errors = defaultdict(list)
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
        try:
            embed = embeds.get_embed(self.curriculum_video)
        except EmbedException:
            errors["curriculum_video"].append("invalid embed URL")
        else:
            if embed.provider_name.lower() != "youtube":
                errors["curriculum_video"].append(
                    "Only YouTube videos are supported for this field "
                )
        if self.staff_link and not self.staff_link_text:
            errors["staff_link_text"].append("Please the text to be used for the link")
        if self.staff_link_text and not self.staff_link:
            errors["staff_link_text"].append("Please add a URL value for the link")
        if self.apply_cta_link and not self.apply_cta_text:
            errors["apply_cta_text"].append("Please add a text value for the CTA link")
        if self.apply_cta_text and not self.apply_cta_link:
            errors["apply_cta_link"].append("Please add a URL value for the CTa")
        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = "dark"

        if int(self.hero_colour_option) == LIGHT_TEXT_ON_DARK_IMAGE:
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
        context["related_staff"] = self.related_staff.select_related("image")

        # If one of the slide in the the programme_galler contains author information
        # we need to set a modifier
        for block in self.programme_gallery:
            if block.value["author"]:
                context["programme_slideshow_modifier"] = "slideshow--author-info"

        # Set the page tab titles
        context["tabs"] = [
            {"title": "Overview"},
            {"title": "Curriculum"},
            {"title": "Requirements"},
            {"title": "Fees & funding"},
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
