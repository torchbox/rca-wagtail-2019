from collections import defaultdict
from itertools import chain

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.text import slugify
from modelcluster.fields import ParentalKey
from rest_framework.fields import CharField as CharFieldSerializer
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.blocks import CharBlock, StructBlock, URLBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Site
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.embeds import embeds
from wagtail.embeds.exceptions import EmbedException
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtailorderable.models import Orderable as WagtailOrdable

from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    FeeBlock,
    GalleryBlock,
    InfoBlock,
    SnippetChooserBlock,
    StepBlock,
)
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    ProgrammeSettings,
    RelatedPage,
)


class DegreeLevel(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class Subject(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.title

    def get_fake_slug(self):
        return slugify(self.title)


def degree_level_serializer(*args, **kwargs):
    """Import the serializer, without a circular import error."""
    from rca.programmes.serializers import DegreeLevelSerializer

    return DegreeLevelSerializer(*args, **kwargs)


class ProgrammePageSubjectPlacement(models.Model):
    page = ParentalKey("ProgrammePage", related_name="subjects")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="programmes",
    )
    panels = [FieldPanel("subject")]


class ProgrammeType(WagtailOrdable):
    display_name = models.CharField(max_length=128)
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.display_name

    def get_fake_slug(self):
        return slugify(self.display_name)


class ProgrammePageRelatedSchoolsAndResearchPages(RelatedPage):
    source_page = ParentalKey(
        "ProgrammePage", related_name="related_schools_and_research_pages"
    )
    panels = [
        PageChooserPanel("page", ["schools.SchoolPage", "research.ResearchCentrePage"])
    ]

    api_fields = [APIField("page")]


class ProgrammePageFeeItem(Orderable):
    page = ParentalKey("ProgrammePage", related_name="fee_items")
    title = models.CharField(
        max_length=120,
        help_text="The title for the information, e.g 'Fees for new students ",
    )
    introduction = models.CharField(
        max_length=1000, help_text="Extra information about the fee items", blank=True
    )
    row = StreamField([("row", FeeBlock())], blank=True)
    panels = [FieldPanel("title"), FieldPanel("introduction"), StreamFieldPanel("row")]

    def __str__(self):
        return self.title


class ProgrammePageRelatedProgramme(RelatedPage):
    source_page = ParentalKey("ProgrammePage", related_name="related_programmes")
    panels = [
        PageChooserPanel(
            "page",
            [
                "programmes.ProgrammePage",
                "guides.GuidePage",
                "shortcourses.ShortCoursePage",
            ],
        )
    ]


class ProgrammePageCareerOpportunities(Orderable):
    page = ParentalKey("ProgrammePage", related_name="career_opportunities")
    text = models.TextField(blank=True, null=True)
    panels = [FieldPanel("text")]


class ProgramPageRelatedStaff(Orderable):
    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    source_page = ParentalKey("ProgrammePage", related_name="related_staff")
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    name = models.CharField(max_length=125, blank=True)
    role = models.CharField(max_length=125, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)
    panels = [
        PageChooserPanel("page", page_type="people.StaffPage"),
        ImageChooserPanel("image"),
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("description"),
        FieldPanel("link"),
    ]

    def __str__(self):
        return self.name


class ProgrammePage(ContactFieldsMixin, BasePage):
    parent_page_types = ["ProgrammeIndexPage"]
    subpage_types = ["guides.GuidePage"]
    template = "patterns/pages/programmes/programme_detail.html"

    # Comments resemble tabbed panels in the editor
    # Content
    degree_level = models.ForeignKey(
        DegreeLevel, on_delete=models.SET_NULL, blank=False, null=True, related_name="+"
    )
    programme_type = models.ForeignKey(
        ProgrammeType,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="+",
    )
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_image_credit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Adding specific credit text here will \
        override the images meta data fields.",
    )
    hero_video = models.URLField(blank=True)
    hero_video_preview_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
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
    programme_description_title = models.CharField(max_length=125, blank=True)
    programme_description_subtitle = models.CharField(max_length=500, blank=True)
    programme_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    programme_video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text="The text dipsplayed next to the video play button",
    )
    programme_video = models.URLField(blank=True)
    programme_description_copy = RichTextField(blank=True)

    programme_gallery = StreamField(
        [("slide", GalleryBlock())], blank=True, verbose_name="Programme gallery"
    )

    # Staff
    staff_link = models.URLField(blank=True)
    staff_link_text = models.CharField(
        max_length=125, blank=True, help_text="E.g. 'See all programme staff'"
    )

    facilities_snippet = models.ForeignKey(
        "utils.FacilitiesSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    facilities_gallery = StreamField(
        [
            (
                "slide",
                StructBlock([("title", CharBlock()), ("image", ImageChooserBlock())]),
            )
        ],
        blank=True,
    )

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
    pathway_blocks = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name="Accordion blocks",
    )
    what_you_will_cover_blocks = StreamField(
        [
            ("accordion_block", AccordionBlockWithTitle()),
            ("accordion_snippet", SnippetChooserBlock("utils.AccordionSnippet")),
        ],
        blank=True,
        verbose_name="Accordion blocks",
    )

    # Requirements
    requirements_text = RichTextField(blank=True)
    requirements_blocks = StreamField(
        [
            ("accordion_block", AccordionBlockWithTitle()),
            ("accordion_snippet", SnippetChooserBlock("utils.AccordionSnippet")),
        ],
        blank=True,
        verbose_name="Accordion blocks",
    )

    # fees
    fees_disclaimer = models.ForeignKey(
        "utils.FeeDisclaimerSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # Scholarships
    scholarships_title = models.CharField(max_length=120)
    scholarships_information = models.CharField(max_length=250)
    scholarship_accordion_items = StreamField(
        [("accordion", AccordionBlockWithTitle())], blank=True
    )
    scholarship_information_blocks = StreamField(
        [("information_block", InfoBlock())], blank=True
    )
    # More information
    more_information_blocks = StreamField(
        [("information_block", InfoBlock())], blank=True
    )

    # Apply
    disable_apply_tab = models.BooleanField(
        default=0,
        help_text=(
            "This setting will remove the apply tab from this programme. "
            "This setting is ignored if the feature has already been disabled"
            " at the global level in Settings > Programme settings."
        ),
    )
    apply_image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    steps = StreamField(
        [
            ("step", StepBlock()),
            ("step_snippet", SnippetChooserBlock("utils.StepSnippet")),
        ],
        blank=True,
    )

    content_panels = BasePage.content_panels + [
        # Taxonomy, relationships etc
        FieldPanel("degree_level"),
        InlinePanel("subjects", label="Subjects"),
        FieldPanel(
            "programme_type",
            help_text="Used to show content related to this programme page",
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel("hero_image"),
                FieldPanel("hero_image_credit"),
                FieldPanel("hero_video"),
                ImageChooserPanel("hero_video_preview_image"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [InlinePanel("related_programmes", label="Related programmes")],
            heading="Related Programmes",
        ),
        MultiFieldPanel(
            [InlinePanel("related_schools_and_research_pages")],
            heading="Related Schools and Research Centres",
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
                ImageChooserPanel("programme_image"),
                FieldPanel("programme_video_caption"),
                FieldPanel("programme_video"),
                FieldPanel("programme_description_copy"),
            ],
            heading="Programme Description",
        ),
        MultiFieldPanel(
            [StreamFieldPanel("programme_gallery")], heading="Programme gallery"
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
                SnippetChooserPanel("facilities_snippet"),
                StreamFieldPanel("facilities_gallery"),
            ],
            heading="Facilities",
        ),
        MultiFieldPanel([StreamFieldPanel("notable_alumni_links")], heading="Alumni"),
        MultiFieldPanel(
            [
                ImageChooserPanel("contact_model_image"),
                FieldPanel("contact_model_url"),
                FieldPanel("contact_model_email"),
                PageChooserPanel("contact_model_form"),
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
        MultiFieldPanel([StreamFieldPanel("pathway_blocks")], heading="Pathways"),
        MultiFieldPanel(
            [StreamFieldPanel("what_you_will_cover_blocks")],
            heading="What you'll cover",
        ),
    ]

    programme_requirements_pannels = [
        FieldPanel("requirements_text"),
        StreamFieldPanel("requirements_blocks"),
    ]
    programme_fees_and_funding_panels = [
        SnippetChooserPanel("fees_disclaimer"),
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
            [FieldPanel("disable_apply_tab")], heading="Apply tab settings"
        ),
        MultiFieldPanel(
            [ImageChooserPanel("apply_image")], heading="Introduction image"
        ),
        MultiFieldPanel([StreamFieldPanel("steps")], heading="Before you begin"),
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

    search_fields = BasePage.search_fields + [
        index.SearchField("programme_description_subtitle", partial_match=True),
        index.AutocompleteField("programme_description_subtitle", partial_match=True),
        index.SearchField("pathway_blocks", partial_match=True),
        index.AutocompleteField("pathway_blocks", partial_match=True),
        index.RelatedFields(
            "programme_type",
            [
                index.SearchField("display_name", partial_match=True),
                index.AutocompleteField("display_name", partial_match=True),
            ],
        ),
        index.RelatedFields(
            "degree_level",
            [
                index.SearchField("title", partial_match=True),
                index.AutocompleteField("title", partial_match=True),
            ],
        ),
        index.RelatedFields(
            "subjects",
            [
                index.RelatedFields(
                    "subject",
                    [
                        index.SearchField("title", partial_match=True),
                        index.AutocompleteField("title", partial_match=True),
                    ],
                )
            ],
        ),
    ]
    api_fields = [
        # Fields for filtering and display, shared with shortcourses.ShortCoursePage.
        APIField("subjects"),
        APIField("programme_type"),
        APIField("related_schools_and_research_pages"),
        APIField(
            "summary",
            serializer=CharFieldSerializer(source="programme_description_subtitle"),
        ),
        APIField(
            name="hero_image_square",
            serializer=ImageRenditionField("fill-580x580", source="hero_image"),
        ),
        # Displayed fields, specific to programmes.
        APIField("degree_level", serializer=degree_level_serializer()),
        APIField("pathway_blocks"),
    ]

    def __str__(self):
        bits = [self.title]
        if self.degree_level:
            bits.append(str(self.degree_level))
        return " ".join(bits)

    def get_admin_display_title(self):
        bits = [self.draft_title]
        if self.degree_level:
            bits.append(str(self.degree_level))
        return " ".join(bits)

    def get_school(self):
        related = self.related_schools_and_research_pages.select_related("page").first()
        if related:
            return related.page

    def clean(self):
        super().clean()
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
        if self.curriculum_video:
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
        if not self.search_description:
            errors["search_description"].append(
                "Please add a search description for the page."
            )
        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
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

        # If one of the slides in the the programme_gallery contains author information
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
        ]
        # Only add the 'apply tab' depending global settings or specific programme page settings
        site = Site.find_for_request(request)
        programme_settings = ProgrammeSettings.for_site(site)
        if not programme_settings.disable_apply_tab and not self.disable_apply_tab:
            context["tabs"].append({"title": "Apply"})

        # Global fields from ProgrammePageGlobalFieldsSettings
        programme_page_global_fields = ProgrammePageGlobalFieldsSettings.for_site(site)
        context["programme_page_global_fields"] = programme_page_global_fields

        # School
        context["programme_school"] = self.get_school()

        return context


class ProgrammeIndexPage(ContactFieldsMixin, BasePage):
    max_count = 1
    subpage_types = ["ProgrammePage", "shortcourses.ShortCoursePage"]
    template = "patterns/pages/programmes/programme_index.html"

    introduction = RichTextField(blank=False, features=["link"])
    search_placeholder_text = models.TextField(blank=True, max_length=120)

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("search_placeholder_text"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information",),
    ]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        subpages = self.get_children().live()
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get("page")
        paginator = Paginator(subpages, per_page)

        try:
            results = paginator.page(page_number)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        # Listing filters
        programme_types = [
            {
                "title": i.display_name,
                "id": i.id,
                "description": i.description,
                "slug": i.get_fake_slug(),
            }
            for i in ProgrammeType.objects.all()
        ]
        subjects = [
            {
                "title": i.title,
                "id": i.id,
                "description": i.description,
                "slug": i.get_fake_slug(),
            }
            for i in Subject.objects.all().order_by("title")
        ]

        schools_and_research_pages = []

        schools_and_research_pages_queryset = chain(
            SchoolPage.objects.live(), ResearchCentrePage.objects.live()
        )
        for i in schools_and_research_pages_queryset:
            description = i.listing_summary
            if hasattr(i, "description"):
                description = i.description
            schools_and_research_pages.append(
                {
                    "title": i.title,
                    "id": i.id,
                    "description": description,
                    "slug": i.slug,
                }
            )

        filters = [
            {"id": "subjects", "title": "Subject", "items": subjects},
            {"id": "programme_type", "title": "Type", "items": programme_types},
            {
                "id": "related_schools_and_research_pages",
                "title": "Schools & centres",
                "items": schools_and_research_pages,
            },
        ]

        context.update(filters=filters)
        context["results"] = results

        return context


@register_setting
class ProgrammePageGlobalFieldsSettings(BaseSetting):
    class Meta:
        verbose_name = "Programme Page Global Fields"

    # Content
    related_content_title = models.CharField(
        max_length=255, default="More opportunities to study at the RCA"
    )
    related_content_subtitle = models.CharField(
        max_length=255, default="Related programmes"
    )
    # Key details
    key_details_next_open_day_title = models.CharField(
        max_length=255, verbose_name="Next open days title", default="Next open day"
    )
    key_details_book_or_view_all_open_days_link_title = models.CharField(
        max_length=255,
        verbose_name="Book open days title",
        default="Book or view all open days",
    )
    key_details_application_deadline_title = models.CharField(
        max_length=255,
        verbose_name="Application deadline title",
        default="Application deadline",
    )
    key_details_career_opportunities_title = models.CharField(
        max_length=255,
        verbose_name="Opportunities title",
        default="Career opportunities",
    )
    key_details_pathways_information_link_title = models.CharField(
        max_length=255,
        verbose_name="Pathways information link title",
        default="Visit the Curriculum tab for more information.",
    )
    # Overview
    alumni_summary_text = models.CharField(
        max_length=255,
        default=(
            "Our alumni form an international network of creative "
            "individuals who have shaped and continue to shape the world."
        ),
    )
    contact_title = models.CharField(max_length=255, default="Ask a question")
    contact_text = models.CharField(
        max_length=255,
        default="Get in touch if you’d like to find out more or have any questions.",
    )
    # Curriculum
    pathways_summary = models.CharField(
        max_length=255,
        default="When applying for this programme, you select one of these specialist pathways.",
    )
    # Requirements
    requirements_introduction = models.CharField(
        max_length=255, default="What you need to know before you apply"
    )
    # Fees
    scholarships_section_title = models.CharField(
        max_length=255, default="Scholarships"
    )
    # Apply
    apply_title = models.CharField(max_length=255, default="Start your application")
    apply_image_title = models.CharField(
        max_length=255, default="Change your life and be here in 2020"
    )
    apply_image_sub_title = models.CharField(
        max_length=255,
        default="The royal college of art welcomes applicants from all over the world",
    )
    apply_cta_link = models.CharField(
        max_length=255, default="https://applications.rca.ac.uk/"
    )
    apply_cta_text = models.CharField(
        max_length=255, default="Visit our applications portal to get started"
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("related_content_title"),
                FieldPanel("related_content_subtitle"),
            ],
            "Related Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("key_details_next_open_day_title"),
                FieldPanel("key_details_book_or_view_all_open_days_link_title"),
                FieldPanel("key_details_application_deadline_title"),
                FieldPanel("key_details_career_opportunities_title"),
                FieldPanel("key_details_pathways_information_link_title"),
            ],
            "Key Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("alumni_summary_text"),
                FieldPanel("contact_title"),
                FieldPanel("contact_text"),
            ],
            "Overview",
        ),
        MultiFieldPanel([FieldPanel("pathways_summary")], "Curriculum"),
        MultiFieldPanel([FieldPanel("requirements_introduction")], "Requirements"),
        MultiFieldPanel([FieldPanel("scholarships_section_title")], "Fees"),
        MultiFieldPanel(
            [
                FieldPanel("apply_title"),
                FieldPanel("apply_image_title"),
                FieldPanel("apply_image_sub_title"),
                FieldPanel("apply_cta_link"),
                FieldPanel("apply_cta_text"),
            ],
            "Apply",
        ),
    ]
