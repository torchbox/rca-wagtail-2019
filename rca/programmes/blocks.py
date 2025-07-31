from django.forms.utils import ErrorList
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class NotableAlumniLinkStructValue(StructValue):
    def get_url(self):
        if link := self.get("link"):
            return link

        if page := self.get("page"):
            return page.specific.url

        return ""

    def is_external_link(self):
        if self.get("link"):
            return True

        return False


class NotableAlumniBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    link = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False)

    def clean(self, value):
        value = super().clean(value)
        errors = {}

        # Make sure link and page does not have a value
        if value["link"] and value["page"]:
            error = ["Both link and page cannot have a value."]
            errors["link"] = errors["page"] = ErrorList(error)

            raise StructBlockValidationError(errors)

        return value

    class Meta:
        icon = "link"
        value_class = NotableAlumniLinkStructValue


class ExperienceStoryBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255, help_text="The title of the story", required=True
    )
    image = ImageChooserBlock(help_text="Featured image for the story", required=True)
    content_type = blocks.CharBlock(
        max_length=100, help_text="e.g. 'Article', 'News', 'Feature'", required=True
    )
    page = blocks.PageChooserBlock(
        help_text="Link to the full story page", required=True
    )

    class Meta:
        icon = "doc-full"
        label = "Story"


class ExperienceStoriesBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255, help_text="The title of the stories", required=False
    )
    stories = blocks.ListBlock(
        ExperienceStoryBlock(), help_text="The stories", min_num=1
    )

    class Meta:
        icon = "doc-full"
        label = "Stories"


class IndividualEmbedBlock(blocks.StructBlock):
    """A single embed with its own caption and source."""

    embed = EmbedBlock(help_text="The embed URL", required=True)
    caption = blocks.CharBlock(
        max_length=255, help_text="The caption for this embed", required=True
    )
    embed_source = blocks.CharBlock(
        max_length=100,
        help_text="The source of this embed (e.g., YouTube, TikTok, Vimeo)",
        required=True,
    )

    class Meta:
        icon = "media"
        label = "Individual Embed"


class SocialEmbedBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
        help_text="The title of the social embeds section",
        required=True,
    )
    embeds = blocks.ListBlock(
        IndividualEmbedBlock(),
        help_text="The embeds with captions",
        min_num=1,
        max_num=12,
    )

    class Meta:
        icon = "code"
        label = "Social Embed"
