from collections import defaultdict
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamBlock, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index

from rca.people.models import AreaOfExpertise
from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    GalleryBlock,
    LinkBlock,
    LinkedImageBlock,
    QuoteBlock,
)
from rca.utils.filter import TabStyleFilter
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    RelatedPage,
    RelatedStaffPageWithManualOptions,
    ResearchTheme,
    ResearchType,
    Sector,
)

from .utils import format_projects_for_gallery


class ProjectPageSectorPlacement(models.Model):
    page = ParentalKey("ProjectPage", related_name="related_sectors")
    sector = models.ForeignKey(
        "utils.Sector", on_delete=models.CASCADE, related_name="projects"
    )
    panels = [FieldPanel("sector")]


class ProjectPageResearchThemePlacement(models.Model):
    page = ParentalKey("ProjectPage", related_name="related_research_themes")
    research_theme = models.ForeignKey(
        "utils.ResearchTheme", on_delete=models.CASCADE, related_name="projects"
    )
    panels = [FieldPanel("research_theme")]


class RelatedProjectPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_project_pages")
    page = models.ForeignKey("projects.ProjectPage", on_delete=models.CASCADE)

    panels = [FieldPanel("page")]


class ProjectPageExpertisePlacement(models.Model):
    page = ParentalKey("ProjectPage", related_name="expertise")
    area_of_expertise = models.ForeignKey(
        "people.AreaOfExpertise", on_delete=models.CASCADE, related_name="projects"
    )
    panels = [FieldPanel("area_of_expertise")]


class ProjectPageRelatedResearchPage(RelatedPage):
    source_page = ParentalKey("ProjectPage", related_name="related_research_pages")
    panels = [PageChooserPanel("page", "research.ResearchCentrePage")]


class ProjectPageRelatedSchoolPage(RelatedPage):
    source_page = ParentalKey("ProjectPage", related_name="related_school_pages")
    panels = [PageChooserPanel("page", "schools.SchoolPage")]


class ProjectPageResearchTypePlacement(Orderable):
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


class ProjectPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/project/project_detail.html"

    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
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
        verbose_name=_("Body copy"),
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
        verbose_name=_("Project PDF"),
    )
    specification_document_link_text = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_("Project PDF link text"),
        help_text=_(
            "You must enter link text if you add a Project PDF, e.g. 'Download project PDF'"
        ),
    )

    gallery = StreamField(
        [("slide", GalleryBlock())],
        blank=True,
        verbose_name=_("Gallery"),
    )
    more_information_title = models.CharField(max_length=80, default="More information")
    more_information = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name=_("More information"),
    )
    partners = StreamField(
        [("link", LinkBlock())],
        blank=True,
        verbose_name=_("Links to partners"),
    )
    funders = StreamField(
        [("link", LinkBlock())],
        blank=True,
        verbose_name=_("Links to funders"),
    )
    quote_carousel = StreamField(
        [("quote", QuoteBlock())],
        blank=True,
        verbose_name=_("Quote carousel"),
    )
    external_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        verbose_name="External Links",
    )
    working_with_heading = models.CharField(blank=True, max_length=120)
    working_with = StreamField(
        StreamBlock([("Collaborator", LinkedImageBlock())], max_num=9),
        blank=True,
        help_text="You can add up to 9 collaborators. Minimum 200 x 200 pixels. \
            Aim for logos that sit on either a white or transparent background.",
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
        index.SearchField("more_information"),
    ]

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("hero_image")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("introduction"),
                FieldPanel("introduction_image"),
                FieldPanel("video"),
                FieldPanel("video_caption"),
            ],
            heading=_("Introduction"),
        ),
        FieldPanel("body"),
        FieldPanel("gallery"),
        MultiFieldPanel(
            [
                FieldPanel("more_information_title"),
                FieldPanel("more_information"),
            ],
            heading=_("More information"),
        ),
        MultiFieldPanel(
            [FieldPanel("working_with_heading"), FieldPanel("working_with")],
            heading="Collaborators",
        ),
        MultiFieldPanel(
            [
                InlinePanel("project_lead", label="Project team lead", max_num=1),
                InlinePanel("related_staff", label="Project team"),
            ],
            "Project team and staff",
        ),
        InlinePanel("related_student_pages", label="Project students"),
        FieldPanel("partners"),
        FieldPanel("funders"),
        FieldPanel("quote_carousel"),
        FieldPanel("external_links"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]

    key_details_panels = [
        InlinePanel("related_sectors", label=_("Innovation RCA sectors")),
        InlinePanel("related_research_themes", label=_("Research themes")),
        InlinePanel("expertise", label=_("RCA Expertise")),
        InlinePanel("related_school_pages", label=_("Related schools")),
        InlinePanel("related_research_pages", label=_("Related research centres")),
        InlinePanel("research_types", label=_("Research types")),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("funding"),
        MultiFieldPanel(
            [
                FieldPanel("specification_document"),
                FieldPanel("specification_document_link_text"),
            ],
            heading="PDF download",
        ),
    ]

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
        return "Project"

    def get_related_projects(self):
        """
        Displays latest projects from the parent School/Centre  the project belongs to.
        IF there are no projects with the same theme School/Centre latest projects with a
        matching research_type will be displayed.
        IF there are no projects with a matching research_type, the latest projects with
        matching expertise tags will be displayed.

        Returns:
            List -- of filtered and formatted ProjectPages
        """

        all_projects = (
            ProjectPage.objects.live()
            .public()
            .not_page(self)
            .order_by("-first_published_at")
        )

        schools = self.related_school_pages.values_list("page_id")
        projects = all_projects.filter(
            related_school_pages__page_id__in=schools
        ).distinct()
        if projects:
            return format_projects_for_gallery(projects)

        research_centres = self.related_research_pages.values_list("page_id")
        projects = all_projects.filter(
            related_research_pages__page_id__in=research_centres
        ).distinct()
        if projects:
            return format_projects_for_gallery(projects)

        research_types = self.research_types.values_list("research_type_id")
        projects = all_projects.filter(
            research_types__research_type_id__in=research_types
        ).distinct()
        if projects:
            return format_projects_for_gallery(projects)

        expertise = self.expertise.values_list("area_of_expertise_id")
        projects = all_projects.filter(
            expertise__area_of_expertise_id__in=expertise
        ).distinct()

        if projects:
            return format_projects_for_gallery(projects)

    def clean(self):
        super().clean()
        errors = defaultdict(list)

        if self.end_date and self.end_date < self.start_date:
            errors["end_date"].append(
                _("Events involving time travel are not supported")
            )
        if self.specification_document and not self.specification_document_link_text:
            errors["specification_document_link_text"].append(
                "You must provide link text for the document"
            )

        if errors:
            raise ValidationError(errors)

    def get_related_school_or_centre(self):
        # returns the first related schools page, if none, return the related research
        # centre page
        related_school = self.related_school_pages.first()
        related_research_page = self.related_research_pages.first()
        if related_school:
            return related_school.page
        elif related_research_page:
            return related_research_page.page

    def get_expertise_linked_filters(self):
        """For the expertise taxonomy thats listed out in key details,
        they need to link to the parent project picker page with a filter pre
        selected"""
        # Get parent page
        parent_picker = ProjectPickerPage.objects.parent_of(self).live().first()
        expertise = []
        for i in self.expertise.all().select_related("area_of_expertise"):
            if parent_picker:
                expertise.append(
                    {
                        "title": i.area_of_expertise.title,
                        "link": f"{parent_picker.url}?expertise={i.area_of_expertise.slug}",
                    }
                )
            else:
                expertise.append({"title": i.area_of_expertise.title})
        return expertise

    def get_sector_linked_filters(self):
        """For the sector taxonomy thats listed out in key details,
        they need to link to the parent project picker page with a filter pre
        selected"""

        parent_picker = ProjectPickerPage.objects.parent_of(self).live().first()
        sectors = []
        for i in self.related_sectors.all().select_related("sector"):
            if parent_picker:
                sectors.append(
                    {
                        "title": i.sector.title,
                        "link": f"{parent_picker.url}?sector={i.sector.slug}",
                    }
                )
            else:
                sectors.append({"title": i.sector.title})
        return sectors

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
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

        context["expertise"] = self.get_expertise_linked_filters()
        context["sectors"] = self.get_sector_linked_filters()
        context["project_lead"] = self.project_lead.select_related("image")
        context["related_staff"] = self.related_staff.select_related("image")
        context["taxonomy_tags"] = taxonomy_tags
        context["related_projects"] = self.get_related_projects()

        return context

    @cached_property
    def is_startup_project(self):
        return len(self.research_types.filter(research_type__title="Start-up")) > 0


class ProjectPickerPage(BasePage):
    template = "patterns/pages/project/project_listing.html"
    introduction = models.CharField(max_length=200, blank=True)
    featured_project = models.ForeignKey(
        "ProjectPage",
        on_delete=models.SET_NULL,
        related_name="featured_project",
        null=True,
        blank=True,
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("featured_project"),
    ]

    def get_active_filters(self, request):
        return {
            "type": request.GET.getlist("research-type"),
            "expertise": request.GET.getlist("expertise"),
            "school_or_centre": request.GET.getlist("school-or-centre"),
        }

    def get_extra_query_params(self, request, active_filters):
        extra_query_params = []
        for filter_name in active_filters:
            for filter_id in active_filters[filter_name]:
                extra_query_params.append(urlencode({filter_name: filter_id}))
        return extra_query_params

    def _format_projects(self, projects):
        """Prepares the queryset into a digestable list for the template"""
        projects_formatted = []
        for page in projects:
            year = None
            if page.start_date:
                year = page.start_date.strftime("%Y")
                if page.end_date and page.end_date.strftime("%Y") != year:
                    end_year = page.end_date.strftime("%Y")
                    year = year + " - " + end_year

            projects_formatted.append(
                {
                    "title": page.title,
                    "image": page.hero_image,
                    "link": page.url,
                    "school": page.get_related_school_or_centre(),
                    "year": year,
                    "listing_summary": page.listing_summary,
                    "meta_heading": page.listing_title,
                }
            )
        return projects_formatted

    def get_base_queryset(self):
        return ProjectPage.objects.child_of(self).live().order_by("-first_published_at")

    def modify_results(self, paginator_page, request):
        for obj in paginator_page.object_list:
            # providing request to get_url() massively improves
            # url generation efficiency, as values are cached
            # on the request
            obj.link = obj.get_url(request)
            obj.image = obj.hero_image
            obj.school = obj.get_related_school_or_centre

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        base_queryset = self.get_base_queryset()
        queryset = base_queryset.all()

        filters = (
            TabStyleFilter(
                "Project type",
                queryset=(
                    ResearchType.objects.filter(
                        id__in=base_queryset.values_list(
                            "research_types__research_type_id", flat=True
                        )
                    )
                ),
                filter_by="research_types__research_type__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Expertise",
                queryset=(
                    AreaOfExpertise.objects.filter(
                        id__in=base_queryset.values_list(
                            "expertise__area_of_expertise_id", flat=True
                        )
                    )
                ),
                filter_by="expertise__area_of_expertise__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
            TabStyleFilter(
                "School or Centre",
                queryset=(
                    Page.objects.live()
                    .filter(
                        content_type__in=list(
                            ContentType.objects.get_for_models(
                                SchoolPage, ResearchCentrePage
                            ).values()
                        )
                    )
                    .filter(
                        models.Q(
                            id__in=base_queryset.values_list(
                                "related_school_pages__page_id", flat=True
                            )
                        )
                        | models.Q(
                            id__in=base_queryset.values_list(
                                "related_research_pages__page_id", flat=True
                            )
                        )
                    )
                ),
                filter_by=(
                    "related_school_pages__page__slug__in",
                    "related_research_pages__page__slug__in",  # Filter by slug here
                ),
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Research theme",
                queryset=(
                    ResearchTheme.objects.filter(
                        id__in=base_queryset.values_list(
                            "related_research_themes__research_theme_id", flat=True
                        )
                    )
                ),
                filter_by="related_research_themes__research_theme__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Sector",
                queryset=(
                    Sector.objects.filter(
                        id__in=base_queryset.values_list(
                            "related_sectors__sector_id", flat=True
                        )
                    )
                ),
                filter_by="related_sectors__sector__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
        )

        # Apply filters
        for f in filters:
            queryset = f.apply(queryset, request.GET)

        # Paginate filtered queryset
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get("page")
        paginator = Paginator(queryset, per_page)
        try:
            results = paginator.page(page_number)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        # Set additional attributes etc
        self.modify_results(results, request)

        # Finalise and return context
        context.update(
            filters={
                "title": "Filter by",
                "aria_label": "Filter results",
                "items": filters,
            },
            results=results,
            result_count=paginator.count,
        )

        # Don't show the featured project if queries are being made
        # or we aren't on the first page of the results
        context["show_featured_project"] = True
        extra_query_params = self.get_extra_query_params(
            request, self.get_active_filters(request)
        )
        if self.featured_project:
            context["featured_project"] = self._format_projects(
                [self.featured_project]
            )[0]
        if extra_query_params or (page_number and page_number != "1"):
            context["show_featured_project"] = False

        return context
