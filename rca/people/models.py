from collections import defaultdict

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
    Orderable,
    Page,
)
from wagtail.search import index

from rca.api_content.content import CantPullFromRcaApi, pull_related_students
from rca.people.filter import SchoolCentreDirectorateFilter
from rca.people.formatters import format_research_highlights
from rca.people.utils import get_staff_research_projects, get_student_research_projects
from rca.programmes.filter import ProgrammeStyleFilter
from rca.programmes.models import ProgrammePage
from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.users.models import User
from rca.utils.blocks import AccordionBlockWithTitle, GalleryBlock, LinkBlock
from rca.utils.filter import TabStyleFilter
from rca.utils.models import BasePage, SluggedTaxonomy

from .admin_forms import StudentPageAdminForm
from .utils import (
    StudentPageInlinePanel,
    StudentPagePromoteTab,
    StudentPageSettingsTab,
    get_area_linked_filters,
)

# PerUserTabbedInterface,

STUDENT_PAGE_RICH_TEXT_FEATURES = features = ["bold", "italic", "link"]


class AreaOfExpertise(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Directorate(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)
    intranet_slug = models.SlugField(
        blank=True,
        help_text="In order to import events and news to the intranet and relate them to this taxonomy, this \
            slug value should match the value of the slug on the Category page on the intranet",
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


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
        AreaOfExpertise,
        on_delete=models.CASCADE,
        related_name="related_staff",
        verbose_name=_("Areas of expertise"),
    )
    panels = [FieldPanel("area_of_expertise")]


class StaffPageDirectorate(models.Model):
    page = ParentalKey("StaffPage", related_name="related_directorates")
    directorate = models.ForeignKey(
        Directorate,
        on_delete=models.CASCADE,
        related_name="related_staff",
        verbose_name=_("Directorates"),
    )
    panels = [FieldPanel("directorate")]


class StaffPageManualRelatedStudents(models.Model):
    page = ParentalKey(
        "people.StaffPage",
        on_delete=models.CASCADE,
        related_name="related_students_manual",
    )
    first_name = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)
    student_page = models.ForeignKey(
        "people.StudentPage",
        on_delete=models.CASCADE,
        related_name="related_programme",
        null=True,
        blank=True,
    )

    panels = [
        FieldPanel("first_name"),
        FieldPanel("surname"),
        FieldPanel("status"),
        FieldPanel("link"),
        FieldPanel("student_page"),
    ]

    def clean(self):
        if self.student_page and any(
            [self.first_name, self.surname, self.status, self.link]
        ):
            raise ValidationError(
                {
                    "student_page": ValidationError(
                        "Please choose between a page or manually entered data"
                    ),
                }
            )


class StaffPage(BasePage):
    template = "patterns/pages/staff/staff_detail.html"
    parent_page_types = ["people.StaffIndexPage"]

    research_profile_url = models.URLField(blank=True)
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
    related_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        verbose_name="Related Links",
    )
    legacy_staff_id = models.IntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Add the legacy staff page ID here to show related students. "
            "This can be found by editing the page on the legacy site and copying "
            "the number from the URL, E.G, /admin/pages/3365/edit"
        ),
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("first_name"),
        index.SearchField("last_name"),
        index.SearchField("body"),
        index.SearchField("more_information"),
    ]

    key_details_panels = [
        InlinePanel(
            "related_research_centre_pages", label=_("Related Research Centres ")
        ),
        InlinePanel("related_schools", label=_("Related Schools")),
        InlinePanel("related_area_of_expertise", label=_("Areas of Expertise")),
        InlinePanel("related_directorates", label=_("Directorate")),
        FieldPanel("research_profile_url", heading=_("Research profile URL")),
    ]

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("staff_title"),
                FieldPanel("first_name"),
                FieldPanel("last_name"),
                FieldPanel("profile_image"),
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
        FieldPanel("gallery"),
        MultiFieldPanel(
            [InlinePanel("related_students_manual"), FieldPanel("legacy_staff_id")],
            heading=_("Related Students"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("more_information_title"),
                FieldPanel("more_information"),
            ],
            heading="More information",
        ),
        FieldPanel("related_links"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    @cached_property
    def meta_title(self):
        bits = []
        if title := self.staff_title.strip():
            bits.append(title)
        if first_name := self.first_name.strip():
            bits.append(first_name)
        if last_name := self.last_name.strip():
            bits.append(last_name)
        return " ".join(bits)

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        return "Staff"

    @property
    def name(self):
        parts = (self.staff_title, self.first_name, self.last_name)
        return " ".join(p for p in parts if p)

    @property
    def related_students_cache_key(self):
        return f"{self.pk}_related_students"

    def fetch_related_students(self):
        value = []
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
        if self.legacy_staff_id:
            # Don't run if there is no ID
            try:
                self.fetch_related_students()
            except CantPullFromRcaApi:
                # Legacy API can be a bit unreliable, so don't
                # break here. The management command can update
                # the value next time it runs
                pass

    def format_student_page(self, page):
        student_page = page
        image = getattr(student_page, "profile_image", None)
        if image:
            image = image.get_rendition("fill-60x60").url
        return {
            "first_name": student_page.first_name,
            "surname": student_page.last_name,
            "status": student_page.degree_status,
            "link": student_page.url,
            "image_url": image,
        }

    def get_related_students(self):
        """
        Returns a list containing:
        - legacy related students from the cached api
        - request and manual related students at the page level
        - Students which reference this page through
        StudentPage.related_supervisor
        """
        students = []

        # Format the api content
        if self.legacy_staff_id:
            for student in self.legacy_related_students:
                item = student
                fullname = student["name"].split(" ")
                item["first_name"] = fullname[0].title()
                # In case we encounter tripple names
                item["surname"] = " ".join(fullname[1:]).title()
                students.append(item)

        # Format students which reference this page through
        # StudentPage.related_supervisor
        students_with_related_supervisor = StudentPage.objects.filter(
            related_supervisor__supervisor_page=self
        ).live()
        for student in students_with_related_supervisor:
            item = self.format_student_page(student)
            students.append(item)

        # Format the students added at the page level
        for student in self.related_students_manual.all():
            if student.student_page:
                student_page = student.student_page.specific
                item = self.format_student_page(student_page)
            else:
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
        for key, value, link in items:
            if key not in regrouped:
                regrouped[key] = {"label": key, "items": [value], "link": link}
            else:
                regrouped[key]["items"].append(value)
            if link and not regrouped[key]["link"]:
                regrouped[key]["link"] = link
        return regrouped.values()

    def get_directorate_linked_filters(self):
        """For the directorate taxonomy thats listed out in key details,
        they need to link to the parent staff picker page with a filter pre
        selected"""

        parent = self.get_parent()
        directorates = []
        for i in self.related_directorates.all().select_related("directorate"):
            if parent:
                directorates.append(
                    {
                        "title": i.directorate.title,
                        "link": f"{parent.url}?school-centre-or-area=d-{i.directorate.slug}",
                    }
                )
            else:
                directorates.append({"title": i.directorate.title})
        return directorates

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        research_pages = get_staff_research_projects(self)
        context["research_highlights"] = format_research_highlights(research_pages)
        context["areas"] = get_area_linked_filters(page=self)
        context["directorates"] = self.get_directorate_linked_filters()
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
            SchoolCentreDirectorateFilter(
                "School, Centre or Area",
                school_queryset=SchoolPage.objects.live().filter(
                    id__in=base_queryset.values_list(
                        "related_schools__page_id", flat=True
                    )
                ),
                centre_queryset=ResearchCentrePage.objects.live().filter(
                    id__in=base_queryset.values_list(
                        "related_research_centre_pages__page_id", flat=True
                    )
                ),
                directorate_queryset=Directorate.objects.filter(
                    id__in=base_queryset.values_list(
                        "related_directorates__directorate_id", flat=True
                    )
                ),
            ),
            ProgrammeStyleFilter(
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
            TabStyleFilter(
                "Expertise",
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


class DegreeType(SluggedTaxonomy):
    pass


class DegreeStatus(SluggedTaxonomy):
    pass


class RelatedStudentPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_student_pages")
    page = models.ForeignKey("people.StudentPage", on_delete=models.CASCADE)

    panels = [FieldPanel("page")]


class StudentPageGallerySlide(Orderable):
    source_page = ParentalKey("StudentPage", related_name="gallery_slides")
    title = models.CharField(max_length=120)
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    author = models.CharField(max_length=120)

    panels = [FieldPanel("image"), FieldPanel("title"), FieldPanel("author")]


class StudentPageSocialLinks(Orderable):
    source_page = ParentalKey("StudentPage", related_name="personal_links")
    link_title = models.CharField(
        max_length=120, help_text="The text displayed for the link"
    )
    url = models.URLField()

    panels = [FieldPanel("link_title"), FieldPanel("url")]


class StudentPageRelatedLinks(Orderable):
    source_page = ParentalKey("StudentPage", related_name="relatedlinks")
    link_title = models.CharField(
        max_length=120, help_text="The text displayed for the link"
    )
    url = models.URLField()

    panels = [FieldPanel("link_title"), FieldPanel("url")]


class StudentPageAreOfExpertisePlacement(models.Model):
    page = ParentalKey("StudentPage", related_name="related_area_of_expertise")
    area_of_expertise = models.ForeignKey(
        AreaOfExpertise,
        on_delete=models.CASCADE,
        related_name="related_student",
        verbose_name=_("Areas of expertise"),
    )
    panels = [FieldPanel("area_of_expertise")]


class StudentPageSupervisor(models.Model):
    page = ParentalKey(
        "people.StudentPage",
        on_delete=models.CASCADE,
        related_name="related_supervisor",
    )
    supervisor_page = models.ForeignKey(
        StaffPage,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )

    title = models.CharField(max_length=20, help_text="E.G, Dr, Mrs, etc", blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)

    panels = [
        HelpPanel(
            content="Choose an internal Staff page or manually enter information"
        ),
        FieldPanel("supervisor_page"),
        FieldPanel("title"),
        FieldPanel("first_name"),
        FieldPanel("surname"),
        FieldPanel("link"),
    ]

    def clean(self):
        errors = defaultdict(list)

        if self.supervisor_page and any(
            [self.title, self.first_name, self.surname, self.link]
        ):
            errors["supervisor_page"].append(
                _(
                    "Please specify a supervisor page or manually enter information, both are not supported"
                )
            )

        if not self.supervisor_page and not self.first_name:
            errors["first_name"].append(_("Please specify a first name"))

        if not self.supervisor_page and not self.surname:
            errors["surname"].append(_("Please specify a surname"))

        if errors:
            raise ValidationError(errors)


class StudentPage(BasePage):
    base_form_class = StudentPageAdminForm
    template = "patterns/pages/student/student_detail.html"
    parent_page_types = ["people.StudentIndexPage"]

    student_title = models.CharField(
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
    degree_status = models.ForeignKey(
        DegreeStatus,
        on_delete=models.SET_NULL,
        related_name="related_student",
        null=True,
        blank=True,
    )
    degree_start_date = models.DateField(blank=True, null=True)
    degree_end_date = models.DateField(blank=True, null=True)
    degree_award = models.CharField(
        max_length=1,
        choices=(("1", "MPhil"), ("2", "PhD")),
        blank=True,
    )
    introduction = models.TextField(blank=True, verbose_name="Project title")
    bio = RichTextField(
        blank=True,
        help_text="Add a detail summary",
        verbose_name="Abstract",
    )
    programme = models.ForeignKey(
        "programmes.ProgrammePage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    biography = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    degrees = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    experience = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    awards = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    funding = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    exhibitions = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    publications = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    research_outputs = RichTextField(
        blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES
    )
    conferences = RichTextField(blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES)
    additional_information_title = models.TextField(blank=True)
    addition_information_content = RichTextField(
        blank=True, features=STUDENT_PAGE_RICH_TEXT_FEATURES
    )
    link_to_final_thesis = models.URLField(blank=True)
    student_funding = RichTextField(blank=True, features=["link"])
    student_user_account = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"groups__name": "Students"},
        unique=True,
    )
    student_user_image_collection = models.OneToOneField(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        unique=True,
        help_text="This should link to this students image collection",
    )
    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("first_name"),
        index.SearchField("last_name"),
        index.SearchField("bio"),
        index.SearchField("biography"),
        index.SearchField("degrees"),
        index.SearchField("experience"),
        index.SearchField("awards"),
        index.SearchField("funding"),
        index.SearchField("exhibitions"),
        index.SearchField("publications"),
        index.SearchField("research_outputs"),
        index.SearchField("addition_information_content"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("student_user_account", permission="superuser"),
        FieldPanel("student_user_image_collection", permission="superuser"),
        MultiFieldPanel(
            [
                FieldPanel("student_title", permission="superuser"),
                FieldPanel("first_name", permission="superuser"),
                FieldPanel("last_name", permission="superuser"),
                FieldPanel("profile_image"),
            ],
            heading="Details",
        ),
        FieldPanel("link_to_final_thesis"),
        InlinePanel("related_supervisor", label="Supervisor information"),
        MultiFieldPanel([FieldPanel("email")], heading="Contact information"),
        FieldPanel("programme", permission="superuser"),
        FieldPanel("degree_start_date", permission="superuser"),
        FieldPanel("degree_end_date", permission="superuser"),
        FieldPanel("degree_award", permission="superuser"),
        FieldPanel("degree_status", permission="superuser"),
        FieldPanel("introduction"),
        FieldPanel("bio"),
        StudentPageInlinePanel(
            "related_project_pages",
            label=_("Project pages"),
            max_num=5,
            heading=_("Research highlights gallery"),
        ),
        InlinePanel("gallery_slides", label="Gallery slide", max_num=5),
        MultiFieldPanel(
            [
                FieldPanel("biography"),
                FieldPanel("degrees"),
                FieldPanel("experience"),
                FieldPanel("awards"),
                FieldPanel("funding"),
                FieldPanel("exhibitions"),
                FieldPanel("publications"),
                FieldPanel("research_outputs"),
                FieldPanel("conferences"),
            ],
            heading="More information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("additional_information_title"),
                FieldPanel("addition_information_content"),
            ],
            heading="Additional information",
        ),
        InlinePanel("relatedlinks", label="External links", max_num=5),
    ]

    key_details_panels = [
        InlinePanel("related_area_of_expertise", label="Areas of Expertise"),
        StudentPageInlinePanel(
            "related_research_centre_pages",
            label=_("Related Research Centres "),
        ),
        StudentPageInlinePanel("related_schools", label=_("Related Schools")),
        InlinePanel("personal_links", label="Personal links", max_num=5),
        FieldPanel("student_funding"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            StudentPagePromoteTab(BasePage.promote_panels, heading="Promote"),
            StudentPageSettingsTab(
                BasePage.settings_panels, heading="Settings"
            ),  # needs to have no content for students
        ]
    )

    @cached_property
    def meta_title(self):
        bits = []
        if title := self.student_title.strip():
            bits.append(title)
        if first_name := self.first_name.strip():
            bits.append(first_name)
        if last_name := self.last_name.strip():
            bits.append(last_name)
        return " ".join(bits)

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        return "Student"

    @property
    def name(self):
        parts = (self.student_title, self.first_name, self.last_name)
        return " ".join(p for p in parts if p)

    @property
    def supervisors(self):
        supervisors = []
        for item in self.related_supervisor.all():
            if item.supervisor_page:
                supervisors.append(
                    {
                        "title": item.supervisor_page.title,
                        "link": item.supervisor_page.url,
                    }
                )
            else:
                supervisors.append(
                    {
                        "title": f"{item.title} {item.first_name} {item.surname}",
                        "link": item.link,
                    }
                )

        return supervisors

    def student_information(self):
        # Method for preparing student data into an accordion friendly format
        data = []
        if self.biography:
            data.append({"value": {"heading": "Biography", "body": self.biography}})
        if self.degrees:
            data.append({"value": {"heading": "Degrees", "body": self.degrees}})
        if self.experience:
            data.append({"value": {"heading": "Experience", "body": self.experience}})
        if self.awards:
            data.append({"value": {"heading": "Awards", "body": self.awards}})
        if self.funding:
            data.append({"value": {"heading": "Funding", "body": self.funding}})
        if self.exhibitions:
            data.append({"value": {"heading": "Exhibitions", "body": self.exhibitions}})
        if self.publications:
            data.append(
                {"value": {"heading": "Publications", "body": self.publications}}
            )
        if self.research_outputs:
            data.append(
                {
                    "value": {
                        "heading": "Research outputs",
                        "body": self.research_outputs,
                    }
                }
            )
        if self.conferences:
            data.append({"value": {"heading": "Conferences", "body": self.conferences}})
        if self.addition_information_content:
            data.append(
                {
                    "value": {
                        "heading": self.additional_information_title
                        or "Additional information",
                        "body": self.addition_information_content,
                    }
                }
            )
        return data

    @property
    def student_gallery(self):
        # Format related model to a nice dict
        data = []
        for item in self.gallery_slides.all():
            data.append(
                {
                    "value": {
                        "title": item.title,
                        "author": item.author,
                        "image": item.image,
                    }
                }
            )
        return data

    @property
    def student_related_links(self):
        return [
            {"value": {"title": item.link_title, "url": item.url}}
            for item in self.relatedlinks.all()
        ]

    def save(self, *args, **kwargs):
        """On saving the student page, make sure the student_user_account
        has a group created with the necessary permissions
        """
        super().save()

        if self.student_user_image_collection and self.student_user_account:

            # Check if a group configuration exsists already for this user.
            group = Group.objects.filter(
                name=self.student_user_account.student_group_name
            )
            if group:
                # If we find a group already, we don't need to create one.
                return

            # Create a specific group for this student so they have edit access to their page
            # and their image collection
            specific_student_group = Group.objects.create(
                name=self.student_user_account.student_group_name
            )

            # Create new add GroupPagePermission
            GroupPagePermission.objects.create(
                group=specific_student_group,
                page=self,
                permission=Permission.objects.get(
                    content_type__app_label="wagtailcore", codename="change_page"
                ),
            )

            # Create new GroupCollectionPermission for Profile Images collection
            GroupCollectionPermission.objects.create(
                group=specific_student_group,
                collection=Collection.objects.get(
                    name=self.student_user_image_collection
                ),
                permission=Permission.objects.get(codename="add_image"),
            )
            GroupCollectionPermission.objects.create(
                group=specific_student_group,
                collection=Collection.objects.get(
                    name=self.student_user_image_collection
                ),
                permission=Permission.objects.get(codename="choose_image"),
            )

            # Add the new specific student group to the user
            self.student_user_account.groups.add(specific_student_group)
            self.student_user_account.save()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        research_pages = get_student_research_projects(self)
        context["areas"] = get_area_linked_filters(page=self)
        context["research_highlights"] = format_research_highlights(research_pages)
        context["related_schools"] = self.related_schools.all()
        context["research_centres"] = self.related_research_centre_pages.all()
        context["student_information"] = self.student_information()
        return context


class StudentIndexPage(BasePage):
    max_count = 1
    subpage_types = ["people.StudentPage"]
    template = "patterns/pages/student/student_index.html"
    introduction = RichTextField(blank=False, features=["link"])
    content_panels = BasePage.content_panels + [FieldPanel("introduction")]
    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_base_queryset(self):
        return (
            StudentPage.objects.child_of(self)
            .live()
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
                "Expertise",
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
                "Degree status",
                queryset=(
                    DegreeStatus.objects.filter(
                        id__in=base_queryset.values_list("degree_status_id", flat=True)
                    )
                ),
                filter_by="degree_status__slug__in",
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
