from rest_framework.fields import Field
from wagtail.models import Page


class EditorialTypeTaxonomySerializer(Field):
    def to_representation(self, value):
        return [
            {"title": v.type.title, "id": v.type.id}
            for v in value.filter(type__isnull=False)
        ]


class RelatedAuthorSerializer(Field):
    def to_representation(self, value):
        return getattr(value, "name", "")


class CTABlockSerializer(Field):
    def to_representation(self, value):
        blocks = []
        for block in value.raw_data:
            page_link = None
            page_title = None
            if block["value"]["page"]:
                page = Page.objects.get(id=block["value"]["page"])
                page_link = page.full_url
                page_title = page.title

            blocks.append(
                {
                    "type": "call_to_action",
                    "value": {
                        "title": block["value"]["title"],
                        "description": block["value"]["description"],
                        "page": block["value"]["page"],
                        "link": {
                            "title": block["value"]["link"]["title"] or page_title,
                            "url": block["value"]["link"]["url"] or page_link,
                        },
                    },
                },
            )
        return blocks
