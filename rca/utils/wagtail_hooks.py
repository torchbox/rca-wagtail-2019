from django.utils.html import escape
from wagtail import hooks
from wagtail.rich_text import LinkHandler

from rca.utils.templatetags.util_tags import is_external
from rca.utils.viewsets import TaxonomiesViewSetGroup


@hooks.register("register_admin_viewset")
def register_taxonomies_viewset_group():
    return TaxonomiesViewSetGroup()


class TargetBlankExternalLinkHandler(LinkHandler):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        target = 'target="_blank"' if is_external(href) else ""
        return f'<a href="{escape(href)}"{target}>'


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(TargetBlankExternalLinkHandler)
