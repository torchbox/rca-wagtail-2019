from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from .content import (
    AccordionBlock,
    CTALinkBlock,
    DocumentBlock,
    ImageBlock,
    ImageVideoGalleryBlock,
    QuoteBlock,
    TableBlock,
)
from .embeds import CookieSnippetBlock, VepplePanoramaBlock, VideoStreamBlock

__all__ = [
    "StoryBlock",
    "GuideBlock",
]


# Main streamfield block to be inherited by Pages
class StoryBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(
        form_classname="full title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()
    quote = QuoteBlock()
    embed = EmbedBlock()
    call_to_action = SnippetChooserBlock(
        "utils.CallToActionSnippet",
        template="patterns/molecules/streamfield/blocks/call_to_action_block.html",
    )
    document = DocumentBlock()
    livestream_video = VideoStreamBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"


# Specific streamfield for the guide pages
class GuideBlock(blocks.StreamBlock):
    anchor_heading = blocks.CharBlock(
        form_classname="full title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/anchor_heading_block.html",
    )
    heading = blocks.CharBlock(
        form_classname="full title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()
    quote = QuoteBlock()
    embed = EmbedBlock(
        label="Embed media",
        help_text="Add a URL from these providers: YouTube, Vimeo, SoundCloud, Twitter.",
    )
    image_video_gallery = ImageVideoGalleryBlock()
    table = TableBlock()
    livestream_video = VideoStreamBlock()
    vepple_panorama = VepplePanoramaBlock()
    cookie_snippet_block = CookieSnippetBlock("utils.CookieButtonSnippet")
    cta_link = CTALinkBlock()
    accordion = AccordionBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
