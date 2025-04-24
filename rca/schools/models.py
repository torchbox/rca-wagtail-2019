import random
from collections import defaultdict

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
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
from wagtail.fields import RichTextField, StreamBlock, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index

from rca.navigation.models import LinkBlock as InternalExternalLinkBlock
from rca.projects.utils import format_projects_for_gallery
from rca.utils.blocks import (
    CallToActionBlock,
    LinkBlock,
    LinkedImageBlock,
    RelatedPageListBlockPage,
    StatisticBlock,
)
from rca.utils.formatters import format_page_teasers, related_list_block_slideshow
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    LegacyNewsAndEventsMixin,
    LinkFields,
    RelatedPage,
    RelatedStaffPageWithManualOptions,
)


class SchoolPagePageStaff(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey("schools.SchoolPage", related_name="related_staff")


class RelatedSchoolPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_schools")
    page = models.ForeignKey("schools.SchoolPage", on_delete=models.CASCADE)
    panels = [FieldPanel("page")]

    api_fields = [
        "page",
    ]


class SchoolPageRelatedShortCourse(RelatedPage):
    source_page = ParentalKey("SchoolPage", related_name="related_short_courses")
    panels = [PageChooserPanel("page", ["shortcourses.ShortCoursePage"])]


class HeroItem(models.Model):
    page = ParentalKey("wagtailcore.Page", related_name="hero_items")
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    panels = [
        FieldPanel("hero_image"),
    ]


class SchoolPageTeaser(models.Model):
    source_page = ParentalKey("SchoolPage", related_name="page_teasers")
    title = models.CharField(max_length=125)
    summary = models.CharField(max_length=250, blank=True)
    pages = StreamField(
        StreamBlock([("Page", RelatedPageListBlockPage(max_num=6))], max_num=1),
    )
    panels = [FieldPanel("title"), FieldPanel("summary"), FieldPanel("pages")]

    def __str__(self):
        return self.title


class SchoolPageStatsBlock(models.Model):
    source_page = ParentalKey("SchoolPage", related_name="stats_block")
    title = models.CharField(max_length=125)
    # statistics = StreamField([("statistic", StatisticBlock(max_num=1))])
    statistics = StreamField(StreamBlock([("statistic", StatisticBlock())], max_num=5))
    background_image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    panels = [
        FieldPanel("title"),
        FieldPanel("background_image"),
        FieldPanel("statistics"),
    ]

    def __str__(self):
        return self.title


class SchoolPageStudentResearch(LinkFields):
    source_page = ParentalKey("schools.SchoolPage", related_name="student_research")
    title = models.CharField(max_length=125)
    slides = StreamField(
        StreamBlock([("Page", RelatedPageListBlockPage())], max_num=1),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("slides"),
        *LinkFields.panels,
    ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.link_page and self.link_url:
            raise ValidationError(
                {
                    "link_url": ValidationError(
                        "You must specify link page or link url. You can't use both."
                    ),
                    "link_page": ValidationError(
                        "You must specify link page or link url. You can't use both."
                    ),
                }
            )

        if self.link_url and not self.link_text:
            raise ValidationError(
                {
                    "link_text": ValidationError(
                        "You must specify link text, if you use the link url field."
                    )
                }
            )


class SchoolPageRelatedProjectPage(Orderable):
    source_page = ParentalKey(
        "schools.SchoolPage", related_name="manually_related_project_pages"
    )
    page = models.ForeignKey("projects.ProjectPage", on_delete=models.CASCADE)

    panels = [FieldPanel("page")]


class StudentPageStudentStories(models.Model):
    source_page = ParentalKey("SchoolPage", related_name="student_stories")
    title = models.CharField(max_length=125)
    slides = StreamField(
        StreamBlock([("Page", RelatedPageListBlockPage())], max_num=1),
    )

    panels = [FieldPanel("title"), FieldPanel("slides")]

    def __str__(self):
        return self.title


class SchoolPage(ContactFieldsMixin, LegacyNewsAndEventsMixin, BasePage):
    template = "patterns/pages/schools/schools.html"
    introduction = RichTextField(blank=False, features=["link"])
    introduction_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This image appears after the intro copy. If a video is uploaded, this image is required",
    )
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text=_("The text displayed next to the video play button"),
    )
    video = models.URLField(blank=True)
    body = RichTextField()

    school_dean = models.ForeignKey(
        "people.StaffPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # location
    location = RichTextField(blank=True, features=["link"])
    next_open_day_date = models.DateField(blank=True, null=True)
    link_to_open_days = models.URLField(blank=True)

    # Get in touch
    get_in_touch = RichTextField(blank=True, features=["link"])
    # Social Links
    social_links = StreamField(
        StreamBlock([("Link", LinkBlock())], max_num=5), blank=True
    )
    news_and_events_heading = models.CharField(blank=True, max_length=120)
    collaborators_heading = models.CharField(blank=True, max_length=120)
    collaborators = StreamField(
        StreamBlock([("Collaborator", LinkedImageBlock())], max_num=9),
        blank=True,
        help_text="You can add up to 9 collaborators. Minimum 200 x 200 pixels. \
            Aim for logos that sit on either a white or transparent background.",
    )
    about_external_links = StreamField(
        [("link", InternalExternalLinkBlock())],
        blank=True,
        verbose_name="External links",
    )
    about_cta_block = StreamField(
        StreamBlock(
            [("call_to_action", CallToActionBlock(label=_("text promo")))], max_num=1
        ),
        verbose_name="CTA",
        blank=True,
    )

    research_projects_title = models.CharField(max_length=125, default="Our Research")
    research_projects_text = RichTextField(blank=True, features=["link"])
    external_links_heading = models.CharField(max_length=125, blank=True)

    external_links = StreamField([("link", InternalExternalLinkBlock())], blank=True)
    research_cta_block = StreamField(
        StreamBlock(
            [("call_to_action", CallToActionBlock(label=_("text promo")))],
            max_num=1,
        ),
        blank=True,
    )
    research_collaborators_heading = models.CharField(blank=True, max_length=120)
    research_collaborators = StreamField(
        StreamBlock([("Collaborator", LinkedImageBlock())], max_num=9),
        blank=True,
        help_text="You can add up to 9 collaborators. Minimum 200 x 200 pixels. \
            Aim for logos that sit on either a white or transparent background.",
    )
    related_programmes_title = models.CharField(blank=True, max_length=120)
    related_programmes_summary = models.CharField(blank=True, max_length=500)
    related_short_courses_title = models.CharField(blank=True, max_length=120)
    related_short_courses_summary = models.CharField(blank=True, max_length=500)
    programmes_links_heading = models.CharField(
        max_length=125, blank=True, verbose_name="Links heading"
    )
    programmes_external_links = StreamField(
        [("link", InternalExternalLinkBlock())],
        blank=True,
        verbose_name="Links",
    )
    programmes_cta_block = StreamField(
        StreamBlock(
            [("call_to_action", CallToActionBlock(label=_("text promo")))],
            max_num=1,
            verbose_name="Call to action",
        ),
        blank=True,
    )

    # Staff
    staff_title = models.CharField(
        blank=True, max_length=120, verbose_name="Related staff title"
    )
    staff_summary = models.CharField(
        blank=True, max_length=500, verbose_name="Related staff summary text"
    )
    staff_external_links = StreamField(
        [("link", InternalExternalLinkBlock())],
        blank=True,
        verbose_name="Links",
    )
    staff_external_links_heading = models.CharField(
        max_length=125, blank=True, verbose_name="Related staff links heading"
    )
    staff_cta_block = StreamField(
        StreamBlock(
            [("call_to_action", CallToActionBlock(label=_("text promo")))],
            max_num=1,
            verbose_name="Call to action",
        ),
        blank=True,
    )
    staff_link = models.URLField(blank=True)
    staff_link_text = models.CharField(
        max_length=125, blank=True, help_text="E.g. 'See all staff'"
    )
    intranet_slug = models.SlugField(
        blank=True,
        help_text="In order to import events and news to the intranet, this \
            slug value should match the category of the School Category on the \
            intranet",
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
        index.SearchField("location"),
        index.SearchField("research_projects_text"),
        index.SearchField("related_programmes_summary"),
        index.SearchField("related_short_courses_summary"),
    ]

    api_fields = [APIField("introduction")]

    # Admin panel configuration
    content_panels = [
        *BasePage.content_panels,
        FieldPanel("intranet_slug"),
        InlinePanel(
            "hero_items",
            max_num=6,
            label="Hero Items",
            help_text="You can add up to 6 hero images",
        ),
        FieldPanel("introduction"),
        FieldPanel("introduction_image"),
        MultiFieldPanel(
            [FieldPanel("video"), FieldPanel("video_caption")], heading="Video"
        ),
        FieldPanel("body"),
    ]
    key_details_panels = [
        FieldPanel("school_dean"),
        MultiFieldPanel(
            [FieldPanel("next_open_day_date"), FieldPanel("link_to_open_days")],
            heading="Next open day",
        ),
        FieldPanel("location", heading="Current location"),
        FieldPanel("get_in_touch"),
        FieldPanel("social_links"),
    ]
    about_panel = [
        InlinePanel("page_teasers", max_num=1, label="Page teasers"),
        MultiFieldPanel(
            [FieldPanel("collaborators_heading"), FieldPanel("collaborators")],
            heading="Collaborators",
        ),
        InlinePanel("stats_block", label="Statistics", max_num=1),
        FieldPanel("about_external_links"),
        FieldPanel("about_cta_block"),
    ]
    news_and_events_panels = [
        FieldPanel("news_and_events_heading"),
        InlinePanel("student_stories", label="Student Stories", max_num=1),
        FieldPanel("legacy_news_and_event_tags"),
    ]
    research_panels = [
        MultiFieldPanel(
            [
                FieldPanel("research_projects_title"),
                FieldPanel("research_projects_text"),
                HelpPanel(
                    content="Projects related to this School are automatically \
                        listed, this can be overriden by defining projects manually"
                ),
                InlinePanel(
                    "manually_related_project_pages", max_num=5, label="Project"
                ),
            ],
            heading="Research projects",
        ),
        MultiFieldPanel(
            [InlinePanel("student_research", label="Student research", max_num=1)],
            heading="Student research",
        ),
        MultiFieldPanel(
            [
                FieldPanel("research_collaborators_heading"),
                FieldPanel("research_collaborators"),
            ],
            heading="Collaborators",
        ),
        MultiFieldPanel(
            [FieldPanel("external_links_heading"), FieldPanel("external_links")],
            heading="Links",
        ),
        MultiFieldPanel([FieldPanel("research_cta_block")], heading="Call To Action"),
    ]
    programmes_panels = [
        FieldPanel("related_programmes_title"),
        FieldPanel("related_programmes_summary"),
    ]
    short_course_panels = [
        FieldPanel("related_short_courses_title"),
        FieldPanel("related_short_courses_summary"),
        InlinePanel("related_short_courses", label="Short Course Pages"),
        MultiFieldPanel(
            [
                FieldPanel("programmes_links_heading"),
                FieldPanel("programmes_external_links"),
            ],
            heading="Links",
        ),
        MultiFieldPanel([FieldPanel("programmes_cta_block")], heading="Call To Action"),
    ]
    staff_panels = [
        FieldPanel("staff_title"),
        FieldPanel("staff_summary"),
        HelpPanel(
            content="By default, related staff will be automatically listed. This \
                can be overriden by adding staff pages here."
        ),
        InlinePanel("related_staff", label="Related staff"),
        MultiFieldPanel(
            [FieldPanel("staff_link_text"), FieldPanel("staff_link")],
            heading="View more staff link",
        ),
        MultiFieldPanel(
            [
                FieldPanel("staff_external_links_heading"),
                FieldPanel("staff_external_links", heading="Links"),
            ],
            heading="Links",
        ),
        FieldPanel("staff_cta_block", heading="Call to action"),
    ]
    contact_panels = [
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Introduction"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(about_panel, heading="About"),
            ObjectList(news_and_events_panels, heading="News and Events"),
            ObjectList(research_panels, heading="Our research"),
            ObjectList(programmes_panels, heading="Programmes"),
            ObjectList(short_course_panels, heading="Short Courses"),
            ObjectList(staff_panels, heading="Staff"),
            ObjectList(contact_panels, heading="Contact"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        return "School"

    def get_hero_image(self):
        # Select a random image from the set of hero items added
        hero_items = self.hero_items.all()
        if not hero_items:
            return
        selected_item = random.choice(hero_items)
        return {
            "image": selected_item.hero_image,
        }

    def clean(self):
        errors = defaultdict(list)
        super().clean()
        if self.staff_link and not self.staff_link_text:
            errors["staff_link_text"].append(_("Missing text value for the link"))
        if self.staff_link_text and not self.staff_link:
            errors["staff_link"].append(_("Missing url value for the link"))
        if errors:
            raise ValidationError(errors)

    def page_nav(self):
        # If these are updated, the id in the template's FE will need to be updated to match
        # TODO conditionally set/remove depending on fields
        return [
            {"title": "Overview"},
            {"title": "Research"},
            {"title": "Study"},
            {"title": "Staff"},
            {"title": "Contact"},
        ]

    def get_related_projects(self):
        """
        Displays latest projects related to this school page.
        Returns:
            List of:
                filtered and formatted manually related ProjectPages
                or automatically fetch project pages from project > school relationship
        """
        from rca.projects.models import ProjectPage

        manual_related_projects = [
            i.page.id
            for i in self.manually_related_project_pages.select_related("page")
        ]
        auto_related_projects = ProjectPage.objects.filter(
            related_school_pages__page_id=self.id
        )[:6]
        if manual_related_projects:
            return format_projects_for_gallery(
                ProjectPage.objects.filter(id__in=manual_related_projects)
            )
        elif auto_related_projects:
            return format_projects_for_gallery(auto_related_projects)

    def get_student_research(self, student_research, request):
        if not student_research:
            return {}
        if student_research.link_page:
            link = student_research.link_page.get_url(request)
        else:
            link = student_research.link_url

        return {
            "title": student_research.title,
            "link_url": link,
            "link_text": student_research.link_text or student_research.link_page,
            "slides": related_list_block_slideshow(student_research.slides),
        }

    def get_student_stories(self, student_stories, request):
        if not student_stories:
            return {}
        return {
            "title": student_stories.title,
            "slides": related_list_block_slideshow(student_stories.slides),
        }

    def get_related_programmes(self):
        """
        Get programme pages from the programme_page__school relationship.
        Returns:
            List -- of filtered and formatted Programme Pages.
        """
        ProgrammePage = apps.get_model("programmes", "ProgrammePage")

        all_programmes = ProgrammePage.objects.live().public()
        return all_programmes.filter(
            related_schools_and_research_pages__page_id=self.id
        ).order_by("title")

    def get_programme_index_link(self):
        ProgrammeIndexPage = apps.get_model("programmes", "ProgrammeIndexPage")
        programme_index = ProgrammeIndexPage.objects.live().first()
        if programme_index:
            return programme_index.get_url()

    def get_short_courses_index_link(self):
        """Returns a link to the programme index page filtered by the
        Short Course ProgrammeType
        """
        ProgrammeType = apps.get_model("programmes", "ProgrammeType")
        short_course_type = ProgrammeType.objects.filter(
            display_name="Short course"
        ).first()
        if short_course_type:
            return (
                f"{self.get_programme_index_link()}?category=programme_types&"
                f"value={short_course_type.id}-{slugify(short_course_type.display_name)}"
            )

    def get_related_staff(self):
        """Method to return a related staff.
        The default behaviour should be to find related staff via the relationship
        from StaffPage > SchoolPage. This also needs to offer the option to
        manually add related staff to the school page, this helps solve issues
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
            StaffPage.objects.filter(related_schools__page=self)
            .live()
            .order_by("last_name")
        ):
            staff.append({"page": item})
        return staff

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        hero_image = self.get_hero_image()
        if hero_image:
            context["hero_image"] = hero_image["image"]
        context["page_teasers"] = format_page_teasers(self.page_teasers.first())
        context["stats_block"] = self.stats_block.select_related(
            "background_image"
        ).first()
        context["featured_research"] = self.get_related_projects()
        context["student_research"] = self.get_student_research(
            self.student_research.first(), request
        )
        context["student_stories"] = self.get_student_stories(
            self.student_stories.first(), request
        )
        context["staff"] = self.get_related_staff()
        # Set the page tab titles for the jump menu
        context["related_programmes"] = [
            {
                "related_items": [
                    page.specific for page in self.get_related_programmes()
                ],
                "link": {
                    "url": self.get_programme_index_link,
                    "title": "Browse all RCA programmes",
                },
            },
        ]

        context["related_short_courses"] = [
            {
                "related_items": [
                    rel.page.specific
                    for rel in self.related_short_courses.select_related("page")
                ],
                "link": {
                    "url": self.get_short_courses_index_link(),
                    "title": "Browse all RCA short courses",
                },
            }
        ]
        # Set the page tab titles for the jump menu
        context["tabs"] = self.page_nav()
        return context
