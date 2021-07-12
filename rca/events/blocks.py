from wagtail.core import blocks

from rca.utils import blocks as utils_blocks


class EventDetailPageBlock(blocks.StreamBlock):
    image = utils_blocks.ImageChooserBlock()
    heading = blocks.CharBlock(
        form_classname="full title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    quote = utils_blocks.QuoteBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"


class CallToAction(blocks.StreamBlock):
    call_to_action = utils_blocks.CallToActionBlock()

