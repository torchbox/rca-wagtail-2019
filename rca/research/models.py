from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.home.models import HERO_COLOUR_CHOICES, LIGHT_TEXT_ON_DARK_IMAGE
from rca.projects.models import ProjectPage
from rca.utils.blocks import LinkBlock
from rca.utils.models import BasePage, RelatedPage, RelatedStaffPageWithManualOptions


class ResearchCentrePageRelatedResearchSpaces(RelatedPage):
    source_page = ParentalKey(
        "research.ResearchCentrePage", related_name="research_spaces"
    )
    panels = [PageChooserPanel("page", ["guides.GuidePage"])]


class ResearchCentrePageRelatedOpportunities(RelatedPage):
    source_page = ParentalKey(
        "research.ResearchCentrePage", related_name="research_opportunities"
    )
    panels = [PageChooserPanel("page", ["guides.GuidePage"])]


class ResearchCentrePageRelatedNews(RelatedPage):
    source_page = ParentalKey(
        "research.ResearchCentrePage", related_name="research_news"
    )
    panels = [PageChooserPanel("page", ["guides.GuidePage", "projects.ProjectPage"])]


class ResearchCentrePageStaff(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey(
        "research.ResearchCentrePage", related_name="related_staff"
    )


class ResearchCentrePage(BasePage):
    template = "patterns/pages/researchcentre/research_centre.html"
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
    introduction = models.TextField(max_length=500, blank=True)
    about_page_url = models.URLField(blank=True)
    about_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    about_page_link_text = models.CharField(blank=True, max_length=120)

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
        help_text=_("The text dipsplayed next to the video play button"),
    )
    video = models.URLField(blank=True)

    primary_staff_url = models.URLField(
        blank=True, help_text=_("The external URL to the staff member page")
    )
    primary_staff_name = models.CharField(
        blank=True, max_length=250, help_text=_("The name of the staff member")
    )
    primary_staff_role = models.CharField(
        blank=True,
        max_length=120,
        help_text=_("The role of the staff member, E.G 'Head of Programme'"),
    )
    centre_address = RichTextField(blank=True)
    centre_tel = PhoneNumberField(blank=True)
    twitter_username = models.CharField(
        blank=True, max_length=15, help_text=_("The Research Centres Twitter username")
    )
    centre_email = models.EmailField(blank=True)
    more_research_centre_content_title = models.CharField(
        blank=True,
        max_length=250,
        help_text=_(
            "The title value displayed above the Research centre news carousel"
        ),
    )
    related_programmes_title = models.CharField(
        max_length=250,
        help_text=_(
            "The title value displayed above the Research centre related_programmes"
        ),
    )
    staff_title = models.CharField(
        blank=True,
        max_length=250,
        help_text=_("The title value displayed above the related staff grid"),
    )
    staff_link = models.URLField(blank=True, help_text=_("Add a link to see all staff"))
    staff_link_text = models.CharField(
        blank=True,
        help_text=_("The text to display on the link to all staff"),
        max_length=80,
    )
    related_links = StreamField(
        [("link", LinkBlock())], blank=True, verbose_name="Related Links"
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [ImageChooserPanel("hero_image"), FieldPanel("hero_colour_option")],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("introduction"),
                ImageChooserPanel("introduction_image"),
                FieldPanel("about_page_url"),
                PageChooserPanel("about_page"),
                FieldPanel("about_page_link_text"),
                FieldPanel("video"),
                FieldPanel("video_caption"),
            ],
            heading=_("Introduction"),
        ),
        MultiFieldPanel(
            [InlinePanel("research_spaces", label="Research spaces")],
            heading="Research spaces",
        ),
        MultiFieldPanel(
            [InlinePanel("research_opportunities", label="Research opportunities")],
            heading="Research opportunities",
        ),
        MultiFieldPanel(
            [
                FieldPanel("more_research_centre_content_title"),
                InlinePanel("research_news", label="Research news"),
            ],
            heading="More research centre content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("staff_title"),
                InlinePanel("related_staff", label="staff"),
                FieldPanel("staff_link"),
                FieldPanel("staff_link_text"),
            ],
            heading="Research Centre Staff",
        ),
        FieldPanel("related_programmes_title"),
        StreamFieldPanel("related_links"),
    ]
    key_details_panels = [
        MultiFieldPanel(
            [
                FieldPanel("primary_staff_name"),
                FieldPanel("primary_staff_url"),
                FieldPanel("primary_staff_role"),
            ],
            heading="Primary staff member",
        ),
        MultiFieldPanel(
            [
                FieldPanel("centre_address"),
                FieldPanel("centre_tel"),
                FieldPanel("centre_email"),
            ],
            heading="Centre contact information",
        ),
        FieldPanel("twitter_username"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def get_child_projects(self):
        """
        Returns a queryset of all child ProjectPages of this page
        TODO: This needs finishing once we have the project pages built
        Also a bit unsure on the template changes I've had to do
        """
        projects = (
            ProjectPage.objects.live()
            .public()
            .descendant_of(self, inclusive=True)
            .select_related("listing_image")
        )
        child_projects = []
        for page in projects:
            page = page.specific
            child_projects.append(
                {
                    "title": page.title,
                    "link": page.url,
                    "image": page.listing_image,
                    "description": page.listing_summary,
                }
            )
        return child_projects

    def get_research_spaces(self):
        research_spaces = []
        for value in self.research_spaces.select_related("page"):
            if value.page.live:
                page = value.page.specific
                research_spaces.append(
                    {
                        "title": page.title,
                        "link": page.url,
                        "image": page.listing_image,
                        "description": page.introduction,
                    }
                )
        return research_spaces

    def get_research_opportunities(self):
        research_opportunities = []
        for value in self.research_opportunities.select_related("page"):
            if value.page.live:
                page = value.page.specific
                research_opportunities.append(
                    {
                        "title": page.title,
                        "link": page.url,
                        "image": page.listing_image,
                        "description": page.listing_summary,
                    }
                )
        return research_opportunities

    def get_research_news(self):
        research_news = {"title": self.more_research_centre_content_title, "slides": []}
        for value in self.research_news.select_related("page"):
            if value.page.live:
                page = value.page.specific
                research_news["slides"].append(
                    {
                        "value": {
                            "title": page.title,
                            "link": page.url,
                            "image": page.listing_image,
                            "summary": page.listing_summary,
                        }
                    }
                )
        return research_news

    def get_related_programme_pages(self):
        from rca.programmes.models import ProgrammePage

        programme_pages_qs = ProgrammePage.objects.filter(
            related_schools_and_research_pages__page_id=self.id
        )
        programme_pages = [
            {
                "title": self.related_programmes_title,
                "related_items": programme_pages_qs,
            }
        ]
        return programme_pages

    def clean(self):
        errors = defaultdict(list)

        if self.twitter_username.startswith("@"):
            self.twitter_username = self.twitter_username[1:]

        if self.about_page and self.about_page_url:
            errors["about_page"].append(
                "Please choose between an internal page, or an external link"
            )
        if (
            self.about_page
            and not self.about_page_link_text
            or self.about_page_url
            and not self.about_page_link_text
        ):
            errors["about_page"].append("Please add some link text for the about page")
        if self.staff_link and not self.staff_link_text:
            errors["staff_link_text"].append(
                "Please add some text for the link to all staff"
            )

        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = "dark"
        if int(self.hero_colour_option) == LIGHT_TEXT_ON_DARK_IMAGE:
            context["hero_colour"] = "light"

        context["about_page"] = self.about_page_url
        if self.about_page:
            context["about_page"] = self.about_page.url

        context["projects"] = self.get_child_projects()
        context["research_spaces"] = self.get_research_spaces()
        context["research_opportunities"] = self.get_research_opportunities()
        context["research_news"] = self.get_research_news()
        context["related_staff"] = self.related_staff.all
        context["related_programmes"] = self.get_related_programme_pages()

        return context
