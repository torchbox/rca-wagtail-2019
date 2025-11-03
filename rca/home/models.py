from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.images import get_image_model_string

from rca.home.blocks import HomePageBodyBlock
from rca.utils.fields import StreamField
from rca.utils.models import (
    DARK_HERO,
    DARK_TEXT_ON_LIGHT_IMAGE,
    HERO_COLOUR_CHOICES,
    LIGHT_HERO,
    BasePage,
    TapMixin,
)


class HomePage(TapMixin, BasePage):
    template = "patterns/pages/home/home_page.html"

    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
    hero_cta_url = models.URLField(blank=True)
    hero_image_credit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Adding specific credit text here will \
        override the images meta data fields.",
    )
    hero_cta_text = models.CharField(max_length=125, blank=True)
    hero_cta_sub_text = models.CharField(max_length=125, blank=True)

    body = StreamField(
        HomePageBodyBlock(),
        blank=True,
    )

    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("hero_image"),
                    FieldPanel("hero_image_credit"),
                    FieldPanel("hero_colour_option"),
                    FieldPanel("hero_cta_url", heading="Hero CTA URL"),
                    FieldPanel("hero_cta_text", heading="Hero CTA Text"),
                    FieldPanel("hero_cta_sub_text", heading="Hero CTA Sub Text"),
                ],
                heading="Hero",
            ),
            FieldPanel("body"),
        ]
        + TapMixin.panels
    )

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def clean(self):
        errors = defaultdict(list)
        if self.hero_cta_url and not self.hero_cta_text:
            errors["hero_cta_text"].append(
                "Please add the text to be displayed as a link"
            )
        if self.hero_cta_text and not self.hero_cta_url:
            errors["hero_cta_url"].append("Please add a URL value")

        if errors:
            raise ValidationError(errors)

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
            next_is_stats = next_block and next_block.block_type in [
                "statistics",
                "promo_banner",
            ]
            backgrounds_match = next_block and next_block.value.get(
                "background_color"
            ) == block.value.get("background_color")

            # Don't display a notch in this section if:
            # - This is the last block in the body.
            # - The next block is a statistics block.
            # - The next block has the same background color as the current block.
            processed_section["should_display_notch"] = not (
                is_last_block or next_is_stats or backgrounds_match
            )

            # If the block is a statistics or a promo banner block, we need to check the
            # previous and next block's background color to determine the background colors
            # for the notch.
            if block.block_type in ["statistics", "promo_banner"]:
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

        context["processed_body"] = self.get_processed_body()

        context["hero_colour"] = LIGHT_HERO

        if (
            hasattr(self, "hero_colour_option")
            and self.hero_colour_option == DARK_TEXT_ON_LIGHT_IMAGE
        ):
            context["hero_colour"] = DARK_HERO

        return context
