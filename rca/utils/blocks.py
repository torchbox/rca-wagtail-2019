from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail.core import blocks
from wagtail.core.blocks.struct_block import StructBlockValidationError
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class FeeBlock(blocks.StructBlock):
    location = blocks.CharBlock(max_length=120, help_text="E.g. Home and EU")
    subsidised = blocks.BooleanBlock(required=False)
    per_year_cost = blocks.CharBlock(
        max_length=120, help_text="E.g. £14,200 per year", required=False
    )
    total_cost = blocks.CharBlock(
        max_length=120, help_text="E.g. £28,400 total fee", required=False
    )


class SlideBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    title = blocks.CharBlock(required=False)
    type = blocks.CharBlock(required=False)
    summary = blocks.TextBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        icon = "plus"


class StatisticBlock(blocks.StructBlock):

    summary = blocks.CharBlock(
        required=False,
        help_text="E.g.  1 in 3 of our graduates are business owners or independent professionals",
    )
    before = blocks.CharBlock(required=False)
    after = blocks.CharBlock(required=False, help_text="E.g. '%'", max_length=2)
    number = blocks.IntegerBlock(required=False, help_text="E.g. '33'")
    meta = blocks.CharBlock(
        required=False, help_text="Small title below the number, e.g 'Nationalities'"
    )

    class Meta:
        icon = "image"


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
    quote = blocks.CharBlock(
        form_classname="title",
        help_text="Enter quote text only, there is no need to add quotation marks",
    )
    author = blocks.CharBlock(required=False)
    job_title = blocks.CharBlock(required=False)

    class Meta:
        icon = "openquote"
        template = "patterns/molecules/streamfield/blocks/quote_block.html"


class LinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    url = blocks.URLBlock(required=False)

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/link_block.html"

    def clean(self, value):
        result = super().clean(value)
        errors = {}

        if value["url"] and not value["title"]:
            errors["title"] = ErrorList(["Please add title value to display."])

        if errors:
            raise ValidationError("Validation error in LinkBlock", params=errors)
        return result


class GalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock()
    author = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    course = blocks.CharBlock(required=False)
    document = DocumentChooserBlock(required=False, help_text="Maximum file size: 10MB")
    video_embed = EmbedBlock(
        help_text="Add a YouTube or Vimeo video URL", required=False
    )
    audio_embed = EmbedBlock(help_text="Add a Soundcloud URL", required=False)

    def clean(self, value):
        result = super().clean(value)
        errors = {}

        if bool(value.get("document")):
            if value.get("document").file_size > 10000000:
                errors["document"] = ErrorList(
                    ["Please ensure your file is below 10MB"]
                )

        if bool(value.get("document")) and bool(value.get("video_embed")):
            errors["document"] = ErrorList(
                ["Multiple values are not supported for Document and Video."]
            )

        if bool(value.get("document")) and bool(value.get("audio_embed")):
            errors["document"] = ErrorList(
                ["Multiple values are not supported for Document and Audio."]
            )

        if bool(value.get("video_embed")) and bool(value.get("audio_embed")):
            errors["video_embed"] = ErrorList(
                ["Multiple values are not supported for Video and Audio."]
            )

        if errors:
            raise StructBlockValidationError(errors)

        return result

    class Meta:
        icon = "image"


class LinkedImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    link = LinkBlock()
    page = blocks.PageChooserBlock(required=False)

    def clean(self, value):
        result = super().clean(value)
        errors = {}

        # Ensure a heading or some preview text has been added
        if value["page"] and value["link"]["url"]:
            errors["page"] = ErrorList(
                ["Please choose between a custom link or a page"]
            )

        if errors:
            raise ValidationError("Validation error in LinkedImageBlock", params=errors)
        return result


class InfoBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(required=False)
    link = LinkBlock()

    class Meta:
        icon = "help"


class StepBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    link = LinkBlock()

    class Meta:
        icon = "list-ol"


class AccordionBlockWithTitle(blocks.StructBlock):
    heading = blocks.CharBlock(
        help_text="A large heading diplayed next to the block", required=False
    )
    preview_text = blocks.CharBlock(
        help_text="The text to display when the accordion is collapsed", required=False
    )
    body = blocks.RichTextBlock(
        help_text="The content shown when the accordion expanded",
        features=["h2", "h3", "bold", "italic", "image", "ul", "ol", "link"],
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


class CustomTeaserBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    meta = blocks.CharBlock(
        required=False, help_text="Small tag value displayed below the title"
    )
    text = blocks.CharBlock(required=False)
    image = ImageChooserBlock()
    link = LinkBlock(required=False)


class RelatedPageListBlockPage(blocks.StreamBlock):
    page = blocks.PageChooserBlock()
    custom_teaser = CustomTeaserBlock()


class RelatedPageListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        help_text="A large heading diplayed at the top of block", required=False
    )
    page = RelatedPageListBlockPage()
    link = LinkBlock(
        help_text="An optional link to display below the expanded content",
        required=False,
    )
    page_link = blocks.PageChooserBlock(required=False)

    def clean(self, value):
        result = super().clean(value)
        errors = {}

        if value["link"]["url"] and value["page_link"]:
            errors["page_link"] = ErrorList(
                ["Please only add a link to a page or an absolute URL"]
            )

        if errors:
            raise ValidationError(
                "Validation error in RelatedPageListBlock", params=errors
            )
        return result


class CallToActionBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        help_text="A large heading diplayed at the top of block", required=False
    )
    description = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    link = LinkBlock(
        help_text="An optional link to display below the expanded content",
        required=False,
    )

    def clean(self, value):
        result = super().clean(value)
        errors = {}

        # Ensure a heading or some preview text has been added
        if value["page"] and value["link"]["url"]:
            errors["page"] = ErrorList(
                ["Please choose between a custom link or a page"]
            )

        if errors:
            raise ValidationError(
                "Validation error in CallToActionBlock", params=errors
            )
        return result


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
    jw_video = JWPLayerBlock()

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
    jw_video = JWPLayerBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
