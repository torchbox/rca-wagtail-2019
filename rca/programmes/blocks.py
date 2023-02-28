from django.forms.utils import ErrorList
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail import blocks

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
