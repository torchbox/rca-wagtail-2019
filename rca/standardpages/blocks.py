from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock

from rca.home.blocks import PromoBannerBlock, StatisticsBlock
from rca.utils.blocks import CTALinkBlock, ImageBlock, QuoteBlock
from rca.utils.blocks.content import CardGridBlock, ImageVideoGalleryBlock


class LandingPageBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(
        form_classname="full title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading_block.html",
    )
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()
    image_video_gallery = ImageVideoGalleryBlock()
    embed = EmbedBlock(
        label="Embed media",
        help_text="Add a URL from these providers: YouTube, Vimeo, SoundCloud, Twitter.",
    )
    cta_link = CTALinkBlock()
    quote = QuoteBlock()
    card_grid = CardGridBlock()


class BodySectionBlock(blocks.StructBlock):
    background_color = blocks.ChoiceBlock(
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
        help_text="Select the background color for this section",
    )
    content = LandingPageBlock(
        required=True,
        help_text="Add content to this section",
    )


class LandingPageBodyBlock(blocks.StreamBlock):
    body_section = BodySectionBlock()
    promo_banner = PromoBannerBlock()
    statistics = StatisticsBlock()
