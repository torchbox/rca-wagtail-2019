from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from rca.utils import blocks as utils_blocks


class EditorialPageBlock(blocks.StreamBlock):
    # There might be editorial pages that uses currently use `image` so we'll want
    # to keep this in here.
    image = ImageChooserBlock()
    image_with_caption = utils_blocks.ImageBlock()
    heading = blocks.CharBlock(
        form_classname="full title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    embed = EmbedBlock()
    quote = utils_blocks.QuoteBlock()
    livestream_video = utils_blocks.VideoStreamBlock()
    cta_link = utils_blocks.CTALinkBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
