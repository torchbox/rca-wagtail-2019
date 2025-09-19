from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock

from rca.utils import blocks as utils_blocks


class DonationPageBlock(blocks.StreamBlock):
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
    image = utils_blocks.ImageBlock()
    quote = utils_blocks.QuoteBlock()
    embed = EmbedBlock(
        label="Embed media",
        help_text="Add a URL from these providers: YouTube, Vimeo, SoundCloud, Twitter.",
    )
    livestream_video = utils_blocks.VideoStreamBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
