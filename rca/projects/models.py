from collections import defaultdict
from urllib.parse import urlencode

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
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
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.blocks import (
    AccordionBlockWithTitle,
    GalleryBlock,
    LinkBlock,
    QuoteBlock,
)
from rca.utils.models import (
    HERO_COLOUR_CHOICES,
    BasePage,
    RelatedPage,
    RelatedStaffPageWithManualOptions,
    ResearchType,
)


class RelatedProjectPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_project_pages")
    page = models.ForeignKey("projects.ProjectPage", on_delete=models.CASCADE)

    panels = [PageChooserPanel("page")]


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
    external_links = StreamField(
        [("link", LinkBlock())], blank=True, verbose_name="External Links"
    )
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
        StreamFieldPanel("external_links"),
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
        InlinePanel("expertise", label=_("RCA Expertise")),
        InlinePanel("related_school_pages", label=_("Related schools")),
        InlinePanel("related_research_pages", label=_("Related research centres")),
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
        matching expertise tags will be displayed.

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

        expertise = self.expertise.values_list("area_of_expertise_id")
        projects = all_projects.filter(
            expertise__area_of_expertise_id__in=expertise
        ).distinct()

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

    def get_related_school(self):
        """ returns the first related schools page"""
        realted_school = self.related_school_pages.first()
        if realted_school:
            return realted_school.page

    def get_expertise_linked_filters(self):
        """ For the expertise taxonomy thats listed out in key details,
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
                        "link": f"{parent_picker.url}?expertise={i.area_of_expertise.id}",
                    }
                )
            else:
                expertise.append({"title": i.area_of_expertise.title})
        return expertise

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
        context["project_lead"] = self.project_lead.select_related("image")
        context["related_staff"] = self.related_staff.select_related("image")
        context["taxonomy_tags"] = taxonomy_tags
        context["related_projects"] = self.get_related_projects()

        return context


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

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        PageChooserPanel("featured_project"),
    ]

    def get_filters(self, active_filters, projects_query):
        # Build a list of filter values that will return results.
        project_filter_field_mapping = {
            "type": "research_types__research_type_id",
            "expertise": "expertise__area_of_expertise_id",
            "school": "related_school_pages__page_id",
            "centre": "related_research_pages__page_id",
        }

        # used_filter_values will equal a dictionary with the same keys as
        # project_filter_field_mapping and the values of each item will be
        # a list of IDs.
        # Example: {
        #     'type': [1,2],
        #     'expertise': [4,8],
        #     'school': [],
        #     'centre': [11,17],
        # }
        used_filter_values = {}
        for project_filter, filter_field in project_filter_field_mapping.items():
            used_filter_values[project_filter] = [
                item[filter_field]
                for item in projects_query.order_by(filter_field)
                .values(filter_field)
                .distinct(filter_field)
                if item[filter_field] is not None
            ]

        from rca.people.models import AreaOfExpertise
        from rca.research.models import ResearchCentrePage
        from rca.schools.models import SchoolPage

        filters = {"title": "Filter by", "items": []}

        research_types = {
            "tab_title": "Research type",
            "filter_name": "type",
            "options": [],
        }
        for i in ResearchType.objects.filter(id__in=used_filter_values["type"]):
            research_types["options"].append(
                {
                    "id": i.id,
                    "title": i.title,
                    "active": str(i.id) in active_filters["type"],
                }
            )
        # Only add if there are options.
        if research_types["options"]:
            filters["items"].append(research_types)

        expertise = {
            "tab_title": "Expertise",
            "filter_name": "expertise",
            "options": [],
        }

        for i in AreaOfExpertise.objects.filter(id__in=used_filter_values["expertise"]):
            expertise["options"].append(
                {
                    "id": i.id,
                    "title": i.title,
                    "active": str(i.id) in active_filters["expertise"],
                }
            )
        # Only add if there are children.
        if expertise["options"]:
            filters["items"].append(expertise)

        school_or_centre = {
            "tab_title": "School or centre",
            "filter_name": "school_or_centre",
            "options": [],
        }
        for i in SchoolPage.objects.live().filter(id__in=used_filter_values["school"]):
            school_or_centre["options"].append(
                {
                    "id": i.id,
                    "title": i.title,
                    "active": str(i.id) in active_filters["school_or_centre"],
                }
            )
        for i in (
            ResearchCentrePage.objects.live()
            .public()
            .filter(id__in=used_filter_values["centre"])
        ):
            school_or_centre["options"].append(
                {
                    "id": i.id,
                    "title": i.title,
                    "active": str(i.id) in active_filters["school_or_centre"],
                }
            )
        # Only add if there are options.
        if school_or_centre["options"]:
            filters["items"].append(school_or_centre)

        return filters

    def _format_results(self, projects):
        """ Prepares the queryset into a digestable list for the template """
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
                    "school": page.get_related_school(),
                    "year": year,
                    "listing_summary": page.listing_summary,
                    "meta_heading": page.listing_title,
                }
            )
        return projects_formatted

    def get_active_filters(self, request):
        return {
            "type": request.GET.getlist("type"),
            "expertise": request.GET.getlist("expertise"),
            "school_or_centre": request.GET.getlist("school_or_centre"),
        }

    def get_extra_query_params(self, request, active_filters):
        extra_query_params = []
        for filter_name in active_filters:
            for filter_id in active_filters[filter_name]:
                extra_query_params.append(urlencode({filter_name: filter_id}))
        return extra_query_params

    def get_projects_query(self):
        return (
            ProjectPage.objects.live()
            .public()
            .descendant_of(self, inclusive=True)
            .select_related("hero_image")
        )

    def get_results(self, request, projects_query, active_filters):
        # Request filters
        research_types = active_filters["type"]
        expertise = active_filters["expertise"]
        school_or_centre = active_filters["school_or_centre"]

        if research_types:
            projects_query = projects_query.filter(
                research_types__research_type_id__in=research_types
            )

        if expertise:
            projects_query = projects_query.filter(
                expertise__area_of_expertise_id__in=expertise
            )

        if school_or_centre:
            projects_query = projects_query.filter(
                models.Q(related_school_pages__page_id__in=school_or_centre)
                | models.Q(related_research_pages__page_id__in=school_or_centre)
            )
        return self._format_results(projects_query.distinct())

    def get_context(self, request, *args, **kwargs):
        page = request.GET.get("page", 1)
        context = super().get_context(request, *args, **kwargs)
        active_filters = self.get_active_filters(request)

        # Send all the query params through to the context so they can be added
        # to the pager links, E.G type=1&type=2&expertise=1...
        context["extra_query_params"] = self.get_extra_query_params(
            request, active_filters
        )

        # Unfiltered Projects query.
        projects_query = self.get_projects_query()

        context["filters"] = self.get_filters(active_filters, projects_query)
        if self.featured_project:
            context["featured_project"] = self._format_results([self.featured_project])[
                0
            ]

        # Don't show the featured project if queries are being made
        # or we aren't on the first page of the results
        context["show_featured_project"] = True
        if context["extra_query_params"] or str(page) != "1":
            context["show_featured_project"] = False

        project_results = self.get_results(request, projects_query, active_filters)

        # Pagination
        paginator = Paginator(project_results, settings.DEFAULT_PER_PAGE)
        try:
            project_results = paginator.page(page)
        except PageNotAnInteger:
            project_results = paginator.page(1)
        except EmptyPage:
            project_results = paginator.page(paginator.num_pages)

        context["results"] = project_results
        context["results_count"] = paginator.count
        return context
