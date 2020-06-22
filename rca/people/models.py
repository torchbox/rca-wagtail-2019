from collections import defaultdict

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
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
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.api_content.content import CantPullFromRcaApi, pull_related_students
from rca.programmes.models import ProgrammePage
from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.utils.blocks import AccordionBlockWithTitle, GalleryBlock, LinkBlock
from rca.utils.filter import TabStyleFilter
from rca.utils.models import BasePage


class AreaOfExpertise(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(AreaOfExpertise, self).save(*args, **kwargs)


class StaffRole(Orderable):
    role = models.CharField(max_length=128)
    programme = models.ForeignKey(
        "programmes.ProgrammePage",
        on_delete=models.CASCADE,
        related_name="related_programme",
        null=True,
        blank=True,
    )
    custom_programme = models.CharField(
        max_length=128,
        help_text=_("Specify a custom programme page here if one does not exist"),
        blank=True,
    )
    page = ParentalKey("StaffPage", related_name="roles")

    def clean(self):
        errors = defaultdict(list)

        if self.programme and self.custom_programme:
            errors["custom_programme"].append(
                _("Please specify only a programme page, or a custom programme")
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.role


class StaffPageAreOfExpertisePlacement(models.Model):
    page = ParentalKey("StaffPage", related_name="related_area_of_expertise")
    area_of_expertise = models.ForeignKey(
        AreaOfExpertise, on_delete=models.CASCADE, related_name="related_staff"
    )
    panels = [FieldPanel("area_of_expertise")]


class StaffPageManualRelatedStudents(models.Model):
    page = ParentalKey(
        "people.StaffPage",
        on_delete=models.CASCADE,
        related_name="related_students_manual",
    )
    first_name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    link = models.URLField(blank=True)

    panels = [
        FieldPanel("first_name"),
        FieldPanel("surname"),
        FieldPanel("status"),
        FieldPanel("link"),
    ]


class StaffPage(BasePage):
    template = "patterns/pages/staff/staff_detail.html"
    parent_page_types = ["people.StaffIndexPage"]

    staff_title = models.CharField(
        max_length=255, help_text=_("E.G Dr, Professor"), blank=True
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    email = models.EmailField(blank=True)
    introduction = models.TextField(blank=True)
    body = RichTextField(blank=True)

    research_highlights_title = models.CharField(
        max_length=120,
        blank=True,
        help_text=_(
            "The title value displayed above the Research highlights gallery showing project pages"
        ),
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
    related_links = StreamField(
        [("link", LinkBlock())], blank=True, verbose_name="Related Links"
    )
    legacy_staff_id = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Add the legacy staff page ID here to show related students"),
    )

    key_details_panels = [
        InlinePanel(
            "related_research_centre_pages", label=_("Related Research Centres ")
        ),
        InlinePanel("related_schools", label=_("Related Schools")),
        InlinePanel("related_area_of_expertise", label=_("Areas of Expertise")),
    ]

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("staff_title"),
                FieldPanel("first_name"),
                FieldPanel("last_name"),
                ImageChooserPanel("profile_image"),
            ],
            heading="Details",
        ),
        InlinePanel("roles", label=_("Staff role")),
        MultiFieldPanel([FieldPanel("email")], heading=_("Contact information")),
        FieldPanel("introduction"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("research_highlights_title"),
                InlinePanel(
                    "related_project_pages", label=_("Project pages"), max_num=8
                ),
            ],
            heading=_("Research highlights gallery"),
        ),
        StreamFieldPanel("gallery"),
        MultiFieldPanel(
            [InlinePanel("related_students_manual"), FieldPanel("legacy_staff_id")],
            heading=_("Related Students"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("more_information_title"),
                StreamFieldPanel("more_information"),
            ],
            heading=_("More information"),
        ),
        StreamFieldPanel("related_links"),
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
    def name(self):
        parts = (self.staff_title, self.first_name, self.last_name)
        return " ".join([p for p in parts if p])

    def format_research_highlights(self):
        """Internal method for formatting related projects to the correct
        structure for the gallery template

        Returns:
            List
        """
        items = []
        for page in self.related_project_pages.all():
            page = page.page.specific
            meta = None
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

    @property
    def related_students_cache_key(self):
        return f"{self.pk}_related_students"

    def fetch_related_students(self):
        value = []
        if self.legacy_staff_id:
            try:
                value = pull_related_students(self.legacy_staff_id)
                cache.set(self.related_students_cache_key, value, None)
            except CantPullFromRcaApi:
                pass
        return value

    @cached_property
    def legacy_related_students(self):
        cached_val = cache.get(self.related_students_cache_key)
        if cached_val is not None:
            return cached_val
        return self.fetch_related_students()

    def save(self, *args, **kwargs):
        """
        Overrides the default Page.save() method to trigger
        a cache refresh for related students (in case the
        legacy_staff_id value has changed).
        """
        super().save(*args, **kwargs)
        try:
            self.fetch_related_students()
        except CantPullFromRcaApi:
            # Legacy API can be a bit unreliable, so don't
            # break here. The management command can update
            # the value next time it runs
            pass

    def get_related_students(self):
        """ Returns a list containing legacy related students from the cached api
        request and manual related students at the page level """
        students = []

        # Format the api content
        for student in self.legacy_related_students:
            item = student
            fullname = student["name"].split(" ")
            item["first_name"] = fullname[0].title()
            # In case we encounter tripple names
            item["surname"] = " ".join(fullname[1:]).title()
            students.append(item)

        # Format the students added at the page level
        for student in self.related_students_manual.all():
            item = {
                "first_name": student.first_name.title(),
                "surname": student.surname.title(),
                "status": student.status,
                "link": student.link,
            }

            students.append(item)

        # Sort students by surname
        students = sorted(students, key=lambda k: k["surname"])

        return students

    def get_roles_grouped(self, request):
        items = []
        # First populate a list of all values
        # E.G [['role title name','programme title'm 'url'], ['role title name','programme title', 'None'], ...]
        for value in self.roles.all().select_related(
            "programme", "programme__degree_level"
        ):
            if value.programme:
                items.append(
                    (str(value.programme), value.role, value.programme.get_url(request))
                )
            else:
                items.append((value.custom_programme, value.role, None))

        # Create a dictionary of values re-using keys so we can group by both
        # the programmes and the custom programmes.
        regrouped = {}
        for (key, value, link) in items:
            if key not in regrouped:
                regrouped[key] = {"label": key, "items": [value], "link": link}
            else:
                regrouped[key]["items"].append(value)
            if link and not regrouped[key]["link"]:
                regrouped[key]["link"] = link
        return regrouped.values()

    def get_area_linked_filters(self):
        """ For the expertise taxonomy thats listed out in key details,
        they need to link to the parent staff picker page with a filter pre
        selected"""

        parent = self.get_parent()
        expertise = []
        for i in self.related_area_of_expertise.all().select_related(
            "area_of_expertise"
        ):
            if parent:
                expertise.append(
                    {
                        "title": i.area_of_expertise.title,
                        "link": f"{parent.url}?area={i.area_of_expertise.slug}",
                    }
                )
            else:
                expertise.append({"title": i.area_of_expertise.title})
        return expertise

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["research_highlights"] = self.format_research_highlights()
        context["areas"] = self.get_area_linked_filters()
        context["related_schools"] = self.related_schools.all()
        context["research_centres"] = self.related_research_centre_pages.all()
        context["related_students"] = self.get_related_students()
        context["roles"] = self.get_roles_grouped(request)
        return context


class StaffIndexPage(BasePage):
    subpage_types = ["people.StaffPage"]
    template = "patterns/pages/staff/staff_index.html"

    introduction = RichTextField(blank=False, features=["link"])

    content_panels = BasePage.content_panels + [FieldPanel("introduction")]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_base_queryset(self):
        return (
            StaffPage.objects.child_of(self)
            .live()
            .prefetch_related("roles")
            .order_by("last_name", "first_name")
        )

    def modify_results(self, paginator_page, request):
        for obj in paginator_page.object_list:
            # providing request to get_url() massively improves
            # url generation efficiency, as values are cached
            # on the request
            obj.link = obj.get_url(request)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        base_queryset = self.get_base_queryset()
        queryset = base_queryset.all()

        filters = (
            TabStyleFilter(
                "School & Centre",
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
                                "related_schools__page_id", flat=True
                            )
                        )
                        | models.Q(
                            id__in=base_queryset.values_list(
                                "related_research_centre_pages__page_id", flat=True
                            )
                        )
                    )
                ),
                filter_by=(
                    "related_schools__page__slug__in",
                    "related_research_centre_pages__page__slug__in",  # Filter by slug here
                ),
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Directorates",
                queryset=(
                    AreaOfExpertise.objects.filter(
                        id__in=base_queryset.values_list(
                            "related_area_of_expertise__area_of_expertise_id", flat=True
                        )
                    )
                ),
                filter_by="related_area_of_expertise__area_of_expertise__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Programme",
                queryset=(
                    ProgrammePage.objects.live().filter(
                        id__in=base_queryset.values_list(
                            "roles__programme_id", flat=True
                        )
                    )
                ),
                filter_by="roles__programme__slug__in",
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
            hero_colour="light",
            filters={
                "title": "Filter by",
                "aria_label": "Filter results",
                "items": filters,
            },
            results=results,
            result_count=paginator.count,
        )
        return context
