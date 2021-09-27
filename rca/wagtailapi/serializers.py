from __future__ import absolute_import, unicode_literals
from collections import OrderedDict

from rest_framework.fields import Field
from wagtail.api.v2.serializers import PageSerializer, get_serializer_class
from wagtail.api.v2.utils import get_full_url
from wagtail.core.models import Page


def get_model_listing_url(context, model):
    url_path = context["router"].get_model_listing_urlpath(model)

    if url_path:
        return get_full_url(context["request"], url_path)


class PageChildrenField(Field):
    """
    Serializes the "children" field.
    Example:
    "children": {
        "count": 1,
        "listing_url": "/api/v2/pages/?child_of=2"
    }
    """

    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        return OrderedDict(
            [
                ("count", page.numchild),
                (
                    "listing_url",
                    get_model_listing_url(self.context, Page)
                    + "?child_of="
                    + str(page.id),
                ),
            ]
        )


class PageDescendantsField(Field):
    """
    Serializes the "descendants" field.
    Example:
    "descendants": {
        "count": 10,
        "listing_url": "/api/v2/pages/?descendant_of=2"
    }
    """

    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        return OrderedDict(
            [
                ("count", page.get_descendants().count()),
                (
                    "listing_url",
                    get_model_listing_url(self.context, Page)
                    + "?descendant_of="
                    + str(page.id),
                ),
            ]
        )


class PageAncestorsField(Field):
    """
    Serializes the "ancestry" field.
    Example:
    "ancestry": [
        {
            "id": 1,
            "meta": {
                "type": "wagtailcore.Page",
                "detail_url": "/api/v2/pages/1/"
            },
            "title": "Root"
        },
        {
            "id": 2,
            "meta": {
                "type": "home.HomePage",
                "detail_url": "/api/v2/pages/2/"
            },
            "title": "Home"
        }
    ]
    """

    def get_attribute(self, instance):
        return instance

    def serialize_page(self, page):
        serializer_class = get_serializer_class(
            page.__class__,
            ["id", "type", "detail_url", "html_url", "title"],
            meta_fields=["type", "detail_url", "html_url"],
            base=PageSerializer,
        )
        serializer = serializer_class(context=self.context)
        return serializer.to_representation(page)

    def to_representation(self, page):
        return [self.serialize_page(ancestor) for ancestor in page.get_ancestors()]


class RCAPageSerializer(PageSerializer):
    children = PageChildrenField(read_only=True)
    descendants = PageDescendantsField(read_only=True)
    ancestors = PageAncestorsField(read_only=True)
