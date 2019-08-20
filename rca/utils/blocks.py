from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "patterns/molecules/streamfield/blocks/image_block.html"


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        template = "patterns/molecules/streamfield/blocks/document_block.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.CharBlock(classname="title")
    attribution = blocks.CharBlock(required=False)

    class Meta:
        icon = "openquote"
        template = "patterns/molecules/streamfield/blocks/quote_block.html"


class LinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    url = blocks.URLBlock(required=False)

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/quote_block.html"


class GalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock()
    author = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    course = blocks.CharBlock(required=False)

    class Meta:
        icon = "image"


class AccordionBlockWithTitle(blocks.StructBlock):
    heading = blocks.CharBlock(
        help_text="A large heading diplayed next to the block", required=False
    )
    preview_text = blocks.CharBlock(
        help_text="The text to display when the accordion is collapsed", required=False
    )
    body = blocks.RichTextBlock(
        help_text="The content shown when the accordion expanded",
        features=["h2", "h3", "bold", "italic", "image"],
    )
    link = LinkBlock(
        help_text="An optional link to display below the expanded content",
        required=False,
    )

    class Meta:
        icon = "list-ul"
        template = "patterns/molecules/accordion/accordion.html"

    def clean(self, value):
        result = super().clean(value)
        errors = {}

        # Ensure a heading or some preview text has been added
        if not value["heading"] and not value["preview_text"]:
            errors["heading"] = ErrorList(
                ["Please add a heading or some prieview text"]
            )

        if errors:
            raise ValidationError(
                "Validation error in AccordionBlockWithTitle", params=errors
            )
        return result


# Main streamfield block to be inherited by Pages
class StoryBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(
        classname="full title",
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

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
