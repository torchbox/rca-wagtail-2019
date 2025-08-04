from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from rca.navigation.models import LinkBlock as InternalExternalLinkBlock

__all__ = [
    "FeeBlock",
    "SlideBlock",
    "StatisticBlock",
    "ImageBlock",
    "DocumentBlock",
    "QuoteBlock",
    "LinkBlock",
    "GalleryBlock",
    "LinkedImageBlock",
    "InfoBlock",
    "StepBlock",
    "AccordionBlockWithTitle",
    "AccordionBlock",
    "CustomTeaserBlock",
    "RelatedPageListBlockPage",
    "RelatedPageListBlock",
    "CallToActionBlock",
    "TableBlock",
    "CTALinkBlock",
]


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
    decorative = blocks.BooleanBlock(
        required=False,
        help_text="Toggle to make image decorative so they can be ignored by assistive technologies.",
    )

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
            raise StructBlockValidationError(errors)
        return result


class GalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    image = ImageChooserBlock()
    author = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    course = blocks.CharBlock(required=False)
    document = DocumentChooserBlock(required=False, help_text="Maximum file size: 10MB")
    video_embed = EmbedBlock(
        help_text="Add a YouTube or Vimeo video URL", required=False
    )
    audio_embed = EmbedBlock(help_text="Add a Soundcloud URL", required=False)
    embed_play_button_label = blocks.TextBlock(
        required=False,
        help_text="The label for the embed play button. If left blank, it will default to 'Play + title'.",
    )

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


class ImageVideoBlock(blocks.StructBlock):
    # This differs from the 'GalleryBlock' as it only allows for an image/video.
    image = ImageChooserBlock()
    video_embed = EmbedBlock(
        required=False,
        help_text="Add a link to embed a video. Leave blank to only display an image.",
    )
    embed_play_button_label = blocks.CharBlock(
        max_length=80,
        required=False,
        help_text="The text displayed below the video.",
        # This is named `embed_play_button_label` to be consistent with `GalleryBlock`.
        label="Caption",
    )

    def clean(self, value):
        cleaned_data = super().clean(value)
        if cleaned_data.get("video_embed") and not cleaned_data.get(
            "embed_play_button_label"
        ):
            raise ValidationError("Caption is required when a video link is provided.")

        return cleaned_data


class ImageVideoGalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    image_video = blocks.StreamBlock(
        [
            ("item", ImageVideoBlock()),
        ],
    )

    class Meta:
        icon = "image"
        template = (
            "patterns/molecules/streamfield/blocks/image_video_gallery_block.html"
        )


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
        features=["h2", "h3", "bold", "italic", "image", "embed", "ul", "ol", "link"],
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


class AccordionBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    items = blocks.ListBlock(AccordionBlockWithTitle())

    class Meta:
        icon = "list-ul"
        template = "patterns/molecules/streamfield/blocks/accordion_block.html"


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


class TableBlock(blocks.StructBlock):
    table = TypedTableBlock(
        [
            ("text", blocks.RichTextBlock(features=["bold", "italic", "link"])),
        ]
    )
    first_row_is_header = blocks.BooleanBlock(
        label="The first row of columns are headers", required=False, default=True
    )
    first_col_is_header = blocks.BooleanBlock(
        label="The first column of each row is a header", required=False, default=False
    )

    class Meta:
        icon = "table"
        template = "patterns/molecules/streamfield/blocks/table_block.html"


class CTALinkBlock(InternalExternalLinkBlock):
    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/cta_link_block.html"
        label = "CTA link"
