from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock

from rca.utils import blocks as utils_blocks


class ScholarshipsListingPageBlock(blocks.StreamBlock):
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
    image = utils_blocks.ImageChooserBlock()
    quote = utils_blocks.QuoteBlock()
    embed = EmbedBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
