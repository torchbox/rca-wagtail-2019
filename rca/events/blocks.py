from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from rca.utils import blocks as utils_blocks


class EventDetailPageBlock(blocks.StreamBlock):
    image = ImageChooserBlock()
    heading = blocks.CharBlock(
        form_classname="full title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    quote = utils_blocks.QuoteBlock()
    embed = EmbedBlock()
    livestream_video = utils_blocks.VideoStreamBlock()
    cta_link = utils_blocks.CTALinkBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"


class CallToAction(blocks.StreamBlock):
    call_to_action = utils_blocks.CallToActionBlock()

    class Meta:
        max_num = 1


class PartnersBlock(blocks.StreamBlock):
    partner = utils_blocks.LinkedImageBlock()

    class Meta:
        max_num = 9
