from django.conf import settings
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

__all__ = [
    "VideoStreamBlock",
    "CookieSnippetBlock",
]


class VideoStreamBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        help_text="Optional title to identify the video. Not shown on the page.",
        required=False,
    )
    video_url = blocks.URLBlock(
        max_length=1000, help_text="The URL of the video to show.", label="Video URL"
    )
    poster_image = ImageChooserBlock(
        help_text="The poster image to show as a placeholder for the video. "
        "For best results use an image 1920x1080 pixels"
    )

    class Meta:
        icon = "media"
        label = "Video Stream Player"
        template = "patterns/molecules/streamfield/blocks/videostream_player_block.html"


class CookieSnippetBlock(SnippetChooserBlock):
    class Meta:
        icon = "snippet"
        template = "patterns/molecules/streamfield/blocks/cookie_snippet_block.html"


class VepplePanoramaBlock(blocks.StructBlock):
    post_id = blocks.IntegerBlock(
        label="Post ID",
        help_text=(
            'NOTE: This is the number from the <code>post="X"</code> part of the embed code '
            "provided by Vepple. Wagtail only needs this ID, and will generate the rest of "
            "the embed code for you."
        ),
    )

    class Meta:
        icon = "view"
        label = "Vepple panorama"
        template = "patterns/molecules/streamfield/blocks/vepple_panorama_block.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["vepple_api_url"] = settings.VEPPLE_API_URL
        return context
