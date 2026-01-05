from collections import defaultdict
from itertools import chain

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models, transaction
from django.db.models import Prefetch
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from rest_framework.fields import CharField as CharFieldSerializer
from taggit.models import TaggedItemBase
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.blocks import CharBlock, StructBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.embeds import embeds
from wagtail.embeds.exceptions import EmbedException
from wagtail.fields import RichTextField, StreamBlock
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable, Site
from wagtail.search import index
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailorderable.models import Orderable as WagtailOrdable

from rca.navigation.models import LinkBlock as InternalExternalLinkBlock
from rca.programmes.blocks import (
    ExperienceStoriesBlock,
    NotableAlumniBlock,
    SocialEmbedBlock,
)
from rca.programmes.utils import format_study_mode, get_accordion_snippet_content
from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    CTALinkBlock,
    FeeBlock,
    GalleryBlock,
    InfoBlock,
    LinkedImageBlock,
    QuoteBlock,
    RelatedPageListBlockPage,
    StepBlock,
)
from rca.utils.fields import StreamField
from rca.utils.formatters import related_list_block_slideshow
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    ProgrammeSettings,
    RelatedPage,
    TapMixin,
)


class DegreeLevel(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class Subject(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=500)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def get_fake_slug(self):
        return slugify(self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


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


class ProgrammePageProgrammeType(models.Model):
    page = ParentalKey("programmes.ProgrammePage", related_name="programme_types")
    programme_type = models.ForeignKey(
        "programmes.ProgrammeType",
        on_delete=models.CASCADE,
    )
    panels = [FieldPanel("programme_type")]

    def __str__(self):
        return self.programme_type.title


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
    panels = [FieldPanel("title"), FieldPanel("introduction"), FieldPanel("row")]

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
        FieldPanel("image"),
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("description"),
        FieldPanel("link"),
    ]

    def __str__(self):
        return self.name


class ProgramPageSocialMediaLinks(Orderable):
    source_page = ParentalKey(
        "programmes.ProgrammePage", related_name="social_media_links"
    )
    link_url = models.URLField(
        verbose_name="Link URL",
    )
    link_text = models.CharField(
        max_length=100,
    )

    panels = [
        FieldPanel("link_url"),
        FieldPanel("link_text"),
    ]

    def __str__(self):
        return f"{self.link_text} » {self.link_url}"


class ProgrammeStoriesBlock(models.Model):
    source_page = ParentalKey("ProgrammePage", related_name="programme_stories")
    title = models.CharField(max_length=125)
    slides = StreamField(
        StreamBlock([("Page", RelatedPageListBlockPage())], max_num=1),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("slides"),
    ]

    def __str__(self):
        return self.title


class ProgrammeStudyModeManager(models.Manager):
    def create(self, **kwargs):
        if self.count() >= 2:
            raise ValueError("Only up to two instances are allowed.")
        with transaction.atomic(using=self.db, savepoint=False):
            return super().create(**kwargs)


class ProgrammeStudyMode(models.Model):
    """
    For instance, full-time, part-time, etc.
    """

    objects = ProgrammeStudyModeManager()

    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None and ProgrammeStudyMode.objects.count() >= 2:
            raise ValueError("Only up to two instances are allowed.")

        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProgrammeStudyModeProgrammePage(models.Model):
    page = ParentalKey("programmes.ProgrammePage", related_name="programme_study_modes")
    programme_study_mode = models.ForeignKey(
        "programmes.ProgrammeStudyMode",
        on_delete=models.CASCADE,
    )
    panels = [FieldPanel("programme_study_mode")]

    api_fields = [APIField("programme_study_mode")]

    def __str__(self):
        return self.programme_study_mode.title

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["page", "programme_study_mode"],
                name="unique_programme_study_mode_per_programme_page",
            )
        ]


class ProgrammeLocation(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProgrammeLocationProgrammePage(models.Model):
    page = ParentalKey("programmes.ProgrammePage", related_name="programme_locations")
    programme_location = models.ForeignKey(
        "programmes.programmeLocation",
        on_delete=models.CASCADE,
    )
    programme_location_url = models.URLField(blank=True)
    panels = [FieldPanel("programme_location"), FieldPanel("programme_location_url")]

    def __str__(self):
        return self.programme_location.title

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["page", "programme_location"],
                name="unique_programme_location_per_programme_page",
            )
        ]


class ProgrammePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "programmes.ProgrammePage",
        on_delete=models.CASCADE,
        related_name="tagged_programme_items",
    )


class ProgrammePage(TapMixin, ContactFieldsMixin, BasePage):
    parent_page_types = ["ProgrammeIndexPage"]
    subpage_types = ["guides.GuidePage"]
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

    next_open_day_date = models.DateField(blank=True, null=True)
    link_to_open_days = models.URLField(blank=True)
    book_or_view_all_open_days_link_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Book open days title",
        default="Book or view all open days",
    )
    application_deadline = models.DateField(blank=True, null=True)
    application_deadline_options = models.CharField(
        max_length=1,
        choices=(
            ("1", "Applications closed, please check back soon"),
            ("2", "Still accepting applications"),
            ("3", "Applications closed"),
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
        [("slide", GalleryBlock())],
        blank=True,
        verbose_name="Programme gallery",
    )

    should_display_stories_above_gallery = models.BooleanField(
        default=False,
        help_text=(
            "Checking this will display the programme stories above the programme gallery"
        ),
    )

    # Staff
    staff_title = models.CharField(
        blank=True,
        max_length=120,
        default="Staff",
        verbose_name="Programme staff title",
    )
    staff_summary = models.CharField(
        blank=True, max_length=500, verbose_name="Related staff summary text"
    )
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
    vepple_post_id = models.IntegerField(
        blank=True,
        null=True,
        help_text=(
            'NOTE: This is the number from the <code>post="X"</code> part of the embed code '
            "provided by Vepple. Wagtail only needs this ID, and will generate the rest of "
            "the embed code for you."
        ),
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
        [("Link_to_person", NotableAlumniBlock())],
        blank=True,
    )

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

    working_with_heading = models.CharField(blank=True, max_length=120)
    working_with = StreamField(
        StreamBlock([("Collaborator", LinkedImageBlock())], max_num=9),
        blank=True,
        help_text="You can add up to 9 collaborators. Minimum 200 x 200 pixels. \
            Aim for logos that sit on either a white or transparent background.",
    )

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
    quote_carousel = StreamField(
        [("quote", QuoteBlock())],
        blank=True,
        verbose_name="Quote carousel",
    )
    quote_carousel_link = StreamField(
        [("link", InternalExternalLinkBlock())],
        blank=True,
        max_num=1,
    )

    # Requirements
    requirements_text = RichTextField(blank=True)
    requirements_video = models.URLField(blank=True)
    requirements_video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text="The text dipsplayed next to the video play button",
    )
    requirements_video_preview_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
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
    qs_code = models.PositiveIntegerField(
        help_text="This code needs to match the name of the codeExternal value in QS, E.G 105",
        blank=True,
        null=True,
    )

    intranet_slug = models.SlugField(
        blank=True,
        help_text="In order to import events and news to the intranet and relate them to this programme, this \
            slug value should match the value of the slug on the Category page on the intranet",
    )
    social_media_links_title = models.CharField(
        verbose_name="Title",
        blank=True,
        max_length=120,
        help_text="The title of the social media links section",
    )

    # Experience
    experience_introduction = models.TextField(
        blank=True,
        help_text="Introductory text for the Experience section",
    )
    experience_cta_link = StreamField(
        [("link", CTALinkBlock())],
        blank=True,
        max_num=1,
        verbose_name="Experience CTA Link",
    )
    experience_content = StreamField(
        [
            ("social_embeds", SocialEmbedBlock()),
            ("story", ExperienceStoriesBlock()),
        ],
        blank=True,
        verbose_name="Experience Content",
        help_text="Add social embeds or editorial page stories",
    )

    tags = ClusterTaggableManager(through=ProgrammePageTag, blank=True)

    content_panels = (
        BasePage.content_panels
        + [
            # Taxonomy, relationships etc
            FieldPanel("degree_level"),
            InlinePanel("subjects", label="Subjects"),
            InlinePanel("programme_types", label="Programme Types"),
            MultiFieldPanel(
                [
                    FieldPanel("hero_image"),
                    FieldPanel("hero_image_credit"),
                    FieldPanel("hero_video"),
                    FieldPanel("hero_video_preview_image"),
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
        + TapMixin.panels
    )
    key_details_panels = [
        MultiFieldPanel(
            [
                FieldPanel("programme_details_credits"),
                FieldPanel("programme_details_credits_suffix"),
                FieldPanel("programme_details_time"),
                FieldPanel("programme_details_time_suffix"),
                InlinePanel(
                    "programme_study_modes",
                    heading="Programme study mode",
                    label="Study mode",
                    max_num=2,
                ),
            ],
            heading="Details",
        ),
        InlinePanel(
            "programme_locations",
            heading="Programme locations",
            label="Location",
        ),
        FieldPanel("next_open_day_date"),
        FieldPanel("link_to_open_days"),
        FieldPanel("book_or_view_all_open_days_link_title"),
        FieldPanel("application_deadline"),
        FieldPanel(
            "application_deadline_options",
            help_text="Optionally display information about the deadline",
        ),
        InlinePanel("career_opportunities", label="Career Opportunities"),
        FieldPanel("programme_specification"),
        MultiFieldPanel(
            [
                FieldPanel("social_media_links_title"),
                InlinePanel(
                    "social_media_links",
                    heading="Links",
                    label="Link",
                    max_num=5,
                ),
            ],
            heading="Social media links",
        ),
    ]
    programme_overview_pannels = [
        MultiFieldPanel(
            [
                FieldPanel("programme_description_title"),
                FieldPanel("programme_description_subtitle"),
                FieldPanel("programme_image"),
                FieldPanel("programme_video_caption"),
                FieldPanel("programme_video"),
                FieldPanel("programme_description_copy"),
            ],
            heading="Programme Description",
        ),
        MultiFieldPanel([FieldPanel("programme_gallery")], heading="Programme gallery"),
        MultiFieldPanel(
            [
                FieldPanel("staff_title"),
                FieldPanel("staff_summary"),
                HelpPanel(
                    content="By default, related staff will be automatically listed. This \
                can be overriden by adding staff pages here."
                ),
                InlinePanel("related_staff"),
                FieldPanel("staff_link"),
                FieldPanel("staff_link_text"),
            ],
            heading="Staff",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facilities_snippet"),
                FieldPanel("vepple_post_id", heading="Vepple post ID"),
                FieldPanel("facilities_gallery"),
            ],
            heading="Facilities",
        ),
        MultiFieldPanel([FieldPanel("notable_alumni_links")], heading="Alumni"),
        InlinePanel("programme_stories", label="Programme Stories", max_num=1),
        FieldPanel("should_display_stories_above_gallery"),
        MultiFieldPanel(
            [
                FieldPanel("contact_model_image"),
                FieldPanel("contact_model_url"),
                FieldPanel("contact_model_email"),
                FieldPanel("contact_model_form"),
            ],
            heading="Contact information",
        ),
    ]
    programme_curriculum_pannels = [
        MultiFieldPanel(
            [
                FieldPanel("curriculum_image"),
                FieldPanel("curriculum_subtitle"),
                FieldPanel("curriculum_video"),
                FieldPanel("curriculum_video_caption"),
                FieldPanel("curriculum_text"),
            ],
            heading="Curriculum introduction",
        ),
        MultiFieldPanel([FieldPanel("pathway_blocks")], heading="Pathways"),
        MultiFieldPanel(
            [FieldPanel("what_you_will_cover_blocks")],
            heading="What you'll cover",
        ),
        MultiFieldPanel(
            [
                FieldPanel("quote_carousel"),
                FieldPanel("quote_carousel_link"),
            ],
            "Quote carousel",
        ),
        MultiFieldPanel(
            [FieldPanel("working_with_heading"), FieldPanel("working_with")],
            "Collaborators",
        ),
    ]

    programme_requirements_pannels = [
        FieldPanel("requirements_text"),
        MultiFieldPanel(
            [
                FieldPanel("requirements_video"),
                FieldPanel("requirements_video_caption"),
                FieldPanel("requirements_video_preview_image"),
            ],
            heading="Video",
        ),
        FieldPanel("requirements_blocks"),
    ]
    programme_fees_and_funding_panels = [
        FieldPanel("fees_disclaimer"),
        MultiFieldPanel(
            [InlinePanel("fee_items", label="Fee items")], heading="For this program"
        ),
        MultiFieldPanel(
            [
                FieldPanel("scholarships_title"),
                FieldPanel("scholarships_information"),
                FieldPanel(
                    "scholarship_accordion_items",
                    help_text="Override the automatically linked scholarships from 'Scholarships' snippets.",
                ),
                FieldPanel("scholarship_information_blocks"),
            ],
            heading="Scholarships",
        ),
        MultiFieldPanel(
            [FieldPanel("more_information_blocks")], heading="More information"
        ),
    ]
    programme_apply_pannels = [
        MultiFieldPanel(
            [FieldPanel("disable_apply_tab")], heading="Apply tab settings"
        ),
        MultiFieldPanel([FieldPanel("apply_image")], heading="Introduction image"),
        MultiFieldPanel([FieldPanel("steps")], heading="Before you begin"),
        FieldPanel("qs_code"),
    ]
    experience_panels = [
        FieldPanel("experience_introduction"),
        FieldPanel("experience_cta_link"),
        FieldPanel("experience_content"),
    ]
    promote_panels = BasePage.promote_panels + [
        MultiFieldPanel(
            [
                HelpPanel(
                    content=(
                        "Adding tags will allow users to search for the programme "
                        "on the programmes listing page by tags"
                    )
                ),
                FieldPanel("tags"),
            ],
            "Programme tags",
        ),
        FieldPanel("intranet_slug"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(programme_overview_pannels, heading="Overview"),
            ObjectList(programme_curriculum_pannels, heading="Curriculum"),
            ObjectList(programme_requirements_pannels, heading="Requirements"),
            ObjectList(programme_fees_and_funding_panels, heading="Fees"),
            ObjectList(experience_panels, heading="Experience"),
            ObjectList(programme_apply_pannels, heading="Apply"),
            ObjectList(promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("programme_description_copy", boost=2),
        index.SearchField("pathway_blocks", boost=2),
        # indexing 'what_you_will_cover_blocks' only works for content in the 'accordion_block' block
        index.SearchField("what_you_will_cover_blocks", boost=2),
        # for content in the 'accordion_snippet' block, we index a custom function
        # https://docs.wagtail.org/en/v5.1.3/topics/search/indexing.html#indexing-callables-and-other-attributes
        index.SearchField("get_what_you_will_cover_blocks_accordion_snippet"),
        index.SearchField("requirements_text"),
        # indexing 'requirements_blocks' only works for content in the 'accordion_block' block
        index.SearchField("requirements_blocks"),
        # for content in the 'accordion_snippet' block, we index a custom function
        # https://docs.wagtail.org/en/v5.1.3/topics/search/indexing.html#indexing-callables-and-other-attributes
        index.SearchField("get_requirements_blocks_accordion_snippet"),
        index.SearchField("scholarship_accordion_items"),
        index.SearchField("scholarship_information_blocks"),
        index.SearchField("more_information_blocks", boost=2),
        index.RelatedFields(
            "programme_types",
            [
                index.RelatedFields(
                    "programme_type", [index.SearchField("display_name")]
                )
            ],
        ),
        index.RelatedFields(
            "programme_locations",
            [index.RelatedFields("programme_location", [index.SearchField("title")])],
        ),
        index.RelatedFields("degree_level", [index.SearchField("title")]),
        index.RelatedFields(
            "subjects",
            [index.RelatedFields("subject", [index.SearchField("title")])],
        ),
        index.RelatedFields(
            "programme_study_modes",
            [index.RelatedFields("programme_study_mode", [index.SearchField("title")])],
        ),
        index.RelatedFields(
            "tagged_programme_items",
            [
                index.RelatedFields(
                    "tag",
                    [
                        index.SearchField("name"),
                        index.AutocompleteField("name"),
                    ],
                )
            ],
        ),
        # Combination of title + degree level.
        index.AutocompleteField("full_title", boost=2),
    ]
    api_fields = [
        # Fields for filtering and display, shared with shortcourses.ShortCoursePage.
        APIField("subjects"),
        APIField("programme_types"),
        APIField("related_schools_and_research_pages"),
        APIField(
            "summary",
            serializer=CharFieldSerializer(source="programme_description_subtitle"),
        ),
        APIField(
            name="hero_image_square",
            serializer=ImageRenditionField("fill-580x580", source="hero_image"),
        ),
        # Additional field(s) for filtering, specific to programmes.
        APIField("programme_study_modes"),
        # Displayed fields, specific to programmes.
        APIField("degree_level", serializer=degree_level_serializer()),
        APIField("pathway_blocks"),
    ]

    def __str__(self):
        bits = [self.title]
        if self.degree_level:
            bits.append(str(self.degree_level))
        return " ".join(bits)

    @property
    def full_title(self):
        return f"{self.title} {self.degree_level.title}"

    @property
    def introduction(self):
        return self.programme_description_subtitle

    @cached_property
    def study_mode(self):
        study_modes = self.programme_study_modes.values_list(
            "programme_study_mode__title", flat=True
        )
        if not study_modes:
            return None
        if len(study_modes) == 1:
            return study_modes[0]

        return format_study_mode(study_modes)

    @cached_property
    def campus_locations(self):
        return self.programme_locations.values(
            "programme_location__title", "programme_location_url"
        ).order_by("programme_location__title")

    def get_admin_display_title(self):
        bits = [self.draft_title]
        if self.degree_level:
            bits.append(str(self.degree_level))
        return " ".join(bits)

    def get_schools(self):
        return self.related_schools_and_research_pages.select_related("page")

    def get_programme_stories(self, programme_stories):
        if not programme_stories:
            return {}
        return {
            "title": programme_stories.title,
            "slides": related_list_block_slideshow(programme_stories.slides),
        }

    def get_related_staff(self):
        """Method to return a related staff.
        The default behaviour should be to find related staff via the relationship
        StaffPage.roles. This also needs to offer the option to
        manually add related staff to the programme page, this helps solve issues
        of custom ordering that's needed with large (>25) staff items.
        """

        from rca.people.models import StaffPage

        related_staff = self.related_staff.select_related("image")
        if related_staff:
            return related_staff

        # For any automatially related staff, adjust the list so we don't have
        # to make edits to the template shared by other page models.
        staff = []
        for item in (
            StaffPage.objects.filter(roles__programme=self).live().order_by("last_name")
        ).distinct():
            staff.append({"page": item})
        return staff

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        return "Programme"

    def get_what_you_will_cover_blocks_accordion_snippet(self):
        """
        We cannot directly index the accordion_snippet block in the what_you_will_cover_blocks
        StreamField. We therefore have to do this manually.

        Ref: https://docs.wagtail.org/en/stable/topics/search/indexing.html#indexing-callables-and-other-attributes
        """

        return get_accordion_snippet_content(self.what_you_will_cover_blocks)

    def get_requirements_blocks_accordion_snippet(self):
        """
        We cannot directly index the accordion_snippet block in the requirements_blocks
        StreamField. We therefore have to do this manually.

        Ref: https://docs.wagtail.org/en/stable/topics/search/indexing.html#indexing-callables-and-other-attributes
        """

        return get_accordion_snippet_content(self.requirements_blocks)

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
        if self.requirements_video and not self.requirements_video_preview_image:
            errors["requirements_video_preview_image"].append(
                "Please add a preview image for the video."
            )
        if self.requirements_video_preview_image and not self.requirements_video:
            errors["requirements_video"].append(
                "Please add a video for the preview image."
            )
        if self.link_to_open_days and not self.book_or_view_all_open_days_link_title:
            errors["book_or_view_all_open_days_link_title"].append(
                "Please specify the 'Book open days title' for the link to open days."
            )
        if errors:
            raise ValidationError(errors)

    @property
    def has_social_media_links(self):
        return self.social_media_links.exists()

    def has_vepple_panorama(self):
        # Insert the script (in `base_page.html`) to load the Vepple panorama, if we have one.
        if self.vepple_post_id:
            return True

        return False

    @cached_property
    def scholarship_items(self):
        """Returns a list of scholarship items for this programme."""
        # Prioritze scholarship_accordion_items, if available
        if self.scholarship_accordion_items:
            return self.scholarship_accordion_items

        # Check for eligible scholarships based on the Scholarship snippet
        if self.scholarship_set.exists():
            # Prefetch related data to avoid n+1 queries
            scholarships = self.scholarship_set.prefetch_related(
                Prefetch(
                    "eligable_programmes",
                    queryset=ProgrammePage.objects.filter(live=True),
                ),
                "other_criteria",
                "fee_statuses",
            ).filter(active=True)

            return [
                {
                    "value": {
                        "heading": s.title,
                        "introduction": s.summary,
                        "eligible_programmes": ", ".join(
                            str(x) for x in s.eligable_programmes.all()
                        ),
                        "other_criteria": ", ".join(
                            x.title for x in s.other_criteria.all()
                        ),
                        "fee_statuses": ", ".join(
                            x.title for x in s.fee_statuses.all()
                        ),
                        "value": s.value,
                    }
                }
                for s in scholarships
            ]

        return []

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
        context["related_staff"] = self.get_related_staff()

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

        # Only add the 'Experience' tab if the experience content is not empty.
        if (
            self.experience_introduction
            or self.experience_introduction
            or self.experience_content
        ):
            context["tabs"].append({"title": "Experience"})

        # Only add the 'apply tab' depending global settings or specific programme page settings
        site = Site.find_for_request(request)
        programme_settings = ProgrammeSettings.for_site(site)
        if not programme_settings.disable_apply_tab and not self.disable_apply_tab:
            context["tabs"].append({"title": "Apply"})

        # Global fields from ProgrammePageGlobalFieldsSettings
        programme_page_global_fields = ProgrammePageGlobalFieldsSettings.for_site(site)
        context["programme_page_global_fields"] = programme_page_global_fields

        # Schools
        context["programme_schools"] = self.get_schools()

        # Stories
        context["programme_stories"] = self.get_programme_stories(
            self.programme_stories.first()
        )

        if self.vepple_post_id:
            context["vepple_api_url"] = settings.VEPPLE_API_URL

        if self.tap_widget:
            context["tap_widget_code"] = mark_safe(self.tap_widget.script_code)

        if self.has_social_media_links:
            context["social_media_links"] = self.social_media_links.all()

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
        MultiFieldPanel(
            [*ContactFieldsMixin.panels],
            heading="Contact information",
        ),
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
            {"id": "programme_types", "title": "Type", "items": programme_types},
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
class ProgrammePageGlobalFieldsSettings(BaseSiteSetting):
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
    alumni_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Page link",
    )
    alumni_cta_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Custom link text",
        help_text="Leave blank to use the page's own title",
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
                FieldPanel("key_details_application_deadline_title"),
                FieldPanel("key_details_career_opportunities_title"),
                FieldPanel("key_details_pathways_information_link_title"),
            ],
            "Key Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("alumni_summary_text"),
                FieldPanel("alumni_cta_link"),
                FieldPanel("alumni_cta_text"),
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
