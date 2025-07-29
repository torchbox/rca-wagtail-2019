from django.forms.utils import ErrorList
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.blocks.struct_block import StructBlockValidationError
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
    title = blocks.CharBlock(max_length=255, help_text="The title of the story")
    image = ImageChooserBlock(help_text="Featured image for the story")
    content_type = blocks.CharBlock(
        max_length=100, help_text="e.g. 'Article', 'News', 'Feature'"
    )
    page = blocks.PageChooserBlock(help_text="Link to the full story page")

    class Meta:
        icon = "doc-full"
        label = "Story"
