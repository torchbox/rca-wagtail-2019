from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

__all__ = [
    "JWPLayerBlock",
    "CookieSnippetBlock",
]


class JWPLayerBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        help_text="Optional title to identify the video. Not shown on the page.",
        required=False,
    )
    video_url = blocks.URLBlock(
        max_length=1000, help_text="The URL of the video to show."
    )
    poster_image = ImageChooserBlock(
        help_text="The poster image to show as a placeholder for the video. "
        "For best results use an image 1920x1080 pixels"
    )

    class Meta:
        icon = "media"
        label = "JW Video Player"
        template = "patterns/molecules/streamfield/blocks/jw_player_block.html"


class CookieSnippetBlock(SnippetChooserBlock):
    class Meta:
        icon = "snippet"
        template = "patterns/molecules/streamfield/blocks/cookie_snippet_block.html"
