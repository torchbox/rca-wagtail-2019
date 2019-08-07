from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import StreamField


class LinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title, required if using a URL",
        required=False,
    )

    def clean(self, value):
        try:
            result = super().clean(value)
        except ValidationError as e:
            errors = e.params
        else:
            errors = {}

        if (value["url"] and value["page"]) or (not value["url"] and not value["page"]):
            errors["url"] = ErrorList(["Please select a URL or a Page"])
        if value["url"] and not value["title"]:
            errors["url"] = ErrorList(["Please set a title when using a URL"])

        if errors:
            raise ValidationError("Validation error in LinkBlock", params=errors)
        return result


class LinkColumnWithHeader(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=False, help_text="Leave blank if no header required."
    )
    links = blocks.ListBlock(LinkBlock())

    class Meta:
        template = ("patterns/molecules/navigation/blocks/footer_column.html",)


class SecondaryLinkBlock(LinkBlock):
    tertiary_links = blocks.ListBlock(LinkBlock())


class QuickLinkBlock(LinkBlock):
    sub_text = blocks.CharBlock(required=False)


class PrimaryNavLink(blocks.StructBlock):
    primary_link = LinkBlock(label="Top level menu links")
    secondary_links = blocks.ListBlock(SecondaryLinkBlock())


@register_setting(icon="list-ul")
class NavigationSettings(BaseSetting, ClusterableModel):

    primary_navigation = StreamField(
        [("link", PrimaryNavLink())], blank=True, help_text="Main site navigation"
    )

    quick_links = StreamField([("link", QuickLinkBlock())], blank=True)

    footer_navigation = StreamField(
        [("column", LinkColumnWithHeader())],
        blank=True,
        help_text="Multiple columns of footer links with optional header.",
    )
    footer_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Single list of elements at the base of the page.",
    )

    panels = [
        StreamFieldPanel("quick_links"),
        StreamFieldPanel("primary_navigation"),
        StreamFieldPanel("footer_navigation"),
        StreamFieldPanel("footer_links"),
    ]
