from django.forms.utils import ErrorList
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.blocks.struct_block import StructBlockValidationError


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
