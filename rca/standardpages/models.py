from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index

from rca.standardpages.blocks import LandingPageBodyBlock
from rca.utils.blocks import StoryBlock
from rca.utils.fields import StreamField as CustomStreamField
from rca.utils.models import BasePage, ProcessedBodyMixin, RelatedPage


class InformationPageRelatedPage(RelatedPage):
    source_page = ParentalKey("InformationPage", related_name="related_pages")


class InformationPage(BasePage):
    is_creatable = False
    template = "patterns/pages/standardpages/information_page.html"

    introduction = models.TextField(blank=True)
    body = StreamField(StoryBlock())

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
        InlinePanel("related_pages", label="Related pages"),
    ]


class IndexPage(BasePage):
    is_creatable = False
    template = "patterns/pages/standardpages/index_page.html"

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [FieldPanel("introduction")]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        subpages = self.get_children().live()
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get("page")
        paginator = Paginator(subpages, per_page)

        try:
            subpages = paginator.page(page_number)
        except PageNotAnInteger:
            subpages = paginator.page(1)
        except EmptyPage:
            subpages = paginator.page(paginator.num_pages)

        context["subpages"] = subpages

        return context


class FlexibleLandingPage(ProcessedBodyMixin, BasePage):
    template = "patterns/pages/standardpages/flexible_landing_page.html"

    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    introduction = RichTextField(blank=True, features=(["bold", "italic"]))
    body = CustomStreamField(
        LandingPageBodyBlock(),
        blank=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("hero_image"),
        FieldPanel("introduction"),
        FieldPanel("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["hero_image"] = self.hero_image

        # Get first background of the first body section
        if self.body:
            first_body_section = self.body[0]
            context["first_body_section_bg"] = first_body_section.value.get(
                "background_color"
            )

        context["processed_body"] = self.get_processed_body()

        return context
