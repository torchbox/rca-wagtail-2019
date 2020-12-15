import random
from collections import defaultdict

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.core.fields import RichTextField, StreamBlock, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.utils.blocks import LinkBlock, LinkedImageBlock, RelatedPageListBlockPage
from rca.utils.models import (
    DARK_HERO,
    DARK_TEXT_ON_LIGHT_IMAGE,
    HERO_COLOUR_CHOICES,
    LIGHT_HERO,
    BasePage,
    LegacyNewsAndEventsMixin,
    LinkFields,
    RelatedPage,
)


class RelatedSchoolPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_schools")
    page = models.ForeignKey("schools.SchoolPage", on_delete=models.CASCADE)

    panels = [PageChooserPanel("page")]


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
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
    panels = [
        ImageChooserPanel("hero_image"),
        FieldPanel("hero_colour_option"),
    ]


class OpenDayLink(LinkFields):
    source_page = ParentalKey("SchoolPage", related_name="open_day_link")


class SchoolPageTeaser(models.Model):
    source_page = ParentalKey("SchoolPage", related_name="page_teasers")
    title = models.CharField(max_length=125)
    summary = models.CharField(max_length=250)
    pages = StreamField(StreamBlock([("Page", RelatedPageListBlockPage(max_num=3))]))

    panels = [FieldPanel("title"), FieldPanel("summary"), StreamFieldPanel("pages")]

    def __str__(self):
        return self.title


class SchoolPage(BasePage):
    template = "patterns/pages/schools/school_page.html"
    introduction = RichTextField(blank=False, features=["link"])
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
    # next open day
    next_open_day_start_date = models.DateField(blank=True, null=True)
    next_open_day_end_date = models.DateField(blank=True, null=True)

    # Get in touch
    get_in_touch = RichTextField(blank=True, features=["link"])
    # Social Links
    social_links = StreamField(
        StreamBlock([("Link", LinkBlock())], max_num=5, required=False)
    )

    collaborators_heading = models.CharField(blank=True, max_length=120)
    collaborators = StreamField(
        StreamBlock([("Collaborator", LinkedImageBlock())], max_num=9, required=False),
        blank=True,
    )

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]
    api_fields = [APIField("introduction")]

    # Admin panel configuration
    content_panels = [
        *BasePage.content_panels,
        InlinePanel("hero_items", max_num=5, label="Hero Items"),
        FieldPanel("introduction"),
        ImageChooserPanel("introduction_image"),
        FieldPanel("video"),
        FieldPanel("video_caption"),
        FieldPanel("body"),
    ]
    key_details_panels = [
        PageChooserPanel("school_dean"),
        MultiFieldPanel(
            [
                FieldPanel("next_open_day_start_date"),
                FieldPanel("next_open_day_end_date"),
                InlinePanel("open_day_link", max_num=1, label="Link"),
            ],
            heading="Next open day",
        ),
        FieldPanel("location"),
        FieldPanel("get_in_touch"),
        StreamFieldPanel("social_links"),
    ]
    about_panel = [
        InlinePanel("page_teasers", max_num=1, label="Page teasers"),
        MultiFieldPanel(
            [FieldPanel("collaborators_heading"), StreamFieldPanel("collaborators")],
            heading="Collaborators",
        ),
    ]
    research_panels = []
    programmes_panels = []
    short_course_panels = []
    staff_panels = []
    contact_panels = []
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Introduction"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(about_panel, heading="About"),
            ObjectList(research_panels, heading="Our research"),
            ObjectList(programmes_panels, heading="Programmes"),
            ObjectList(programmes_panels, heading="Short Courses"),
            ObjectList(staff_panels, heading="Staff"),
            ObjectList(contact_panels, heading="Contact"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def get_hero_image(self):
        # Select a random image from the set of hero items added
        hero_items = self.hero_items.all()
        if not hero_items:
            return
        selected_item = random.choice(hero_items)
        return {
            "image": selected_item.hero_image,
            "hero_colour": selected_item.hero_colour_option,
        }

    def clean(self):
        errors = defaultdict(list)
        super().clean()
        if self.next_open_day_end_date and not self.next_open_day_start_date:
            errors["next_open_day_start_date"].append(
                _("If you enter an end date, you must also enter a start date")
            )

        if (
            self.next_open_day_end_date
            and self.next_open_day_end_date < self.next_open_day_start_date
        ):
            errors["next_open_day_end_date"].append(
                _("Events involving time travel are not supported")
            )

        if errors:
            raise ValidationError(errors)

    def page_nav(self):
        # TODO conditionally set/remove depending on fields
        return [
            {"title": "About"},
            {"title": "Our research"},
            {"title": "Programmes"},
            {"title": "Short Courses"},
            {"title": "Staff"},
            {"title": "Contact"},
        ]

    def format_page_teasers(self, obj):
        if not obj:
            return
        page_teasers = {"title": obj.title, "summary": obj.summary, "pages": []}
        for item in obj.pages:
            for block in item.value:
                if block.block_type == "custom_teaser":
                    page_teasers["pages"].append(
                        {
                            "title": block.value["title"],
                            "description": block.value["text"],
                            "image": block.value["image"],
                            "link": block.value["link"]["url"],
                            "type": block.value["meta"],
                        }
                    )
                elif block.block_type == "page":
                    page = block.value.specific
                    summary = (
                        page.introduction
                        if hasattr(page, "introduction")
                        else page.listing_summary
                    )
                    image = (
                        page.hero_image
                        if hasattr(page, "hero_image")
                        else page.listing_image
                    )
                    page_teasers["pages"].append(
                        {
                            "title": page.title,
                            "description": summary,
                            "image": image,
                            "link": page.url,
                        }
                    )

        return page_teasers

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # We're picking the hero from multiple objects so we need to override
        # the BasePage hero_colour option
        hero_image = self.get_hero_image()
        if hero_image:
            context["hero_image"] = hero_image["image"]
            context["hero_colour"] = LIGHT_HERO
            if (
                hero_image["hero_colour"]
                and hero_image["hero_colour"] == DARK_TEXT_ON_LIGHT_IMAGE
            ):
                context["hero_colour"] = DARK_HERO
        context["open_day_link"] = self.open_day_link.first()
        context["page_teasers"] = self.format_page_teasers(self.page_teasers.first())

        # Set the page tab titles for the jump menu
        context["tabs"] = self.page_nav()
        return context
