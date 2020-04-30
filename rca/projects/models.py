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
    PageChooserPanel,
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
from rca.utils.models import (
    BasePage,
    RelatedPage,
    RelatedStaffPageWithManualOptions,
    ResearchType,
)


class ProjectPageSubjectPlacement(models.Model):
    page = ParentalKey("ProjectPage", related_name="subjects")
    subject = models.ForeignKey(
        "programmes.Subject", on_delete=models.CASCADE, related_name="projects"
    )
    panels = [FieldPanel("subject")]


class ProjectPageRelatedResearchPage(RelatedPage):
    source_page = ParentalKey("ProjectPage", related_name="related_research_pages")
    panels = [PageChooserPanel("page", "research.ResearchCentrePage")]


class ProjectPageRelatedSchoolPage(RelatedPage):
    source_page = ParentalKey("ProjectPage", related_name="related_school_pages")
    panels = [PageChooserPanel("page", "schools.SchoolPage")]


class ProjectPageResearchTypePlacement(models.Model):
    page = ParentalKey("ProjectPage", related_name="research_types")
    research_type = models.ForeignKey(
        ResearchType,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="projects",
    )
    panels = [FieldPanel("research_type")]


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
    more_information_title = models.CharField(max_length=80, default="More information")
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
        MultiFieldPanel(
            [
                FieldPanel("more_information_title"),
                StreamFieldPanel("more_information"),
            ],
            heading=_("More information"),
        ),
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
        InlinePanel("subjects", label=_("RCA Experties")),
        InlinePanel("related_school_pages", label=_("Related schools")),
        InlinePanel("related_research_pages", label=_("Related research cetnres")),
        InlinePanel("research_types", label=_("Research types")),
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

    def _format_projects_for_gallery(self, projects):
        """Internal method for formatting related projects to the correct
        structure for the gallery template

        Arguments:
            projects: Queryset of project pages to format

        Returns:
            List: Maximum of 8 projects
        """
        items = []
        for page in projects[:8]:
            page = page.specific
            meta = ""
            related_school = page.related_school_pages.first()
            if related_school is not None:
                meta = related_school.page.title

            items.append(
                {
                    "title": page.title,
                    "link": page.url,
                    "image": page.hero_image,
                    "description": page.introduction,
                    "meta": meta,
                }
            )
        return items

    def get_related_projects(self):
        """
        Displays latest projects from the parent School/Centre  the project belongs to.
        IF there are no projects with the same theme School/Centre latest projects with a
        matching research_type will be displayed.
        IF there are no projects with a matching research_type, the latest projects with
        matching subject tags will be displayed.

        Returns:
            List -- of filtered and formatted ProjectPages
        """

        all_projects = ProjectPage.objects.live().public().not_page(self)

        schools = self.related_school_pages.values_list("page_id")
        projects = all_projects.filter(
            related_school_pages__page_id__in=schools
        ).distinct()
        if projects:
            return self._format_projects_for_gallery(projects)

        research_centres = self.related_research_pages.values_list("page_id")
        projects = all_projects.filter(
            related_research_pages__page_id__in=research_centres
        ).distinct()
        if projects:
            return self._format_projects_for_gallery(projects)

        research_types = self.research_types.values_list("research_type_id")
        projects = all_projects.filter(
            research_types__research_type_id__in=research_types
        ).distinct()
        if projects:
            return self._format_projects_for_gallery(projects)

        subjects = self.subjects.values_list("subject_id")
        projects = all_projects.filter(subjects__subject_id__in=subjects).distinct()

        if projects:
            return self._format_projects_for_gallery(projects)

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
        taxonomy_tags = []
        if self.related_school_pages:
            for i in self.related_school_pages.all():
                taxonomy_tags.append({"title": i.page.title})
        if self.related_research_pages:
            for i in self.related_research_pages.all():
                taxonomy_tags.append({"title": i.page.title})
        if self.research_types:
            for i in self.research_types.all():
                taxonomy_tags.append({"title": i.research_type.title})

        context["subjects"] = subjects
        context["project_lead"] = self.project_lead.select_related("image")
        context["related_staff"] = self.related_staff.select_related("image")
        context["taxonomy_tags"] = taxonomy_tags
        context["related_projects"] = self.get_related_projects()

        return context


class ProjectPickerPage(BasePage):
    pass
