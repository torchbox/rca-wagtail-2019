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
from rca.utils.models import BasePage, RelatedPage


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


class FlexibleLandingPage(BasePage):
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

    def get_processed_body(self):
        # Processes the body streamfield to determine when and what notches are displayed.
        processed_body = []
        num_blocks = len(self.body)

        for i, block in enumerate(self.body):
            processed_section = {
                "block": block,
            }

            previous_block = self.body[i - 1] if i > 0 else None
            next_block = self.body[i + 1] if (i + 1) < num_blocks else None

            is_last_block = next_block is None
            next_is_promo_banner = next_block and next_block.block_type in [
                "promo_banner"
            ]
            backgrounds_match = next_block and next_block.value.get(
                "background_color"
            ) == block.value.get("background_color")

            # Don't display a notch in this section if:
            # - This is the last block in the body.
            # - The next block has the same background color as the current block.
            processed_section["should_display_notch"] = not (
                is_last_block or next_is_promo_banner or backgrounds_match
            )

            # If the block is a promo banner block, we need to check the
            # previous and next block's background color to determine the background colors
            # for the notch.
            if block.block_type in ["promo_banner"]:
                if previous_block and previous_block.block_type == "body_section":
                    processed_section["previous_block_bg"] = previous_block.value.get(
                        "background_color"
                    )

                if next_block and next_block.block_type == "body_section":
                    processed_section["next_block_bg"] = next_block.value.get(
                        "background_color"
                    )

            processed_body.append(processed_section)

        return processed_body

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
