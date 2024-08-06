from django.db import models
from wagtail.api import APIField
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.search import index


class CustomImage(AbstractImage):
    alt = models.CharField(max_length=255)
    creator = models.CharField(max_length=255, blank=True)
    year = models.CharField(max_length=4, blank=True)
    medium = models.CharField(max_length=255, blank=True)
    photographer = models.CharField(max_length=255, blank=True)
    dimensions = models.CharField(max_length=20, blank=True)
    permission = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        "alt",
        "creator",
        "year",
        "medium",
        "photographer",
        "dimensions",
        "permission",
    )
    api_fields = [
        APIField("alt"),
        APIField("creator"),
        APIField("year"),
        APIField("medium"),
        APIField("photographer"),
        APIField("dimensions"),
        APIField("permission"),
        APIField("focal_point_x"),
        APIField("focal_point_y"),
        APIField("focal_point_width"),
        APIField("focal_point_height"),
    ]

    search_fields = AbstractImage.search_fields + [
        index.SearchField("creator"),
        index.SearchField("photographer"),
    ]


class Rendition(AbstractRendition):
    image = models.ForeignKey(
        "CustomImage", related_name="renditions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
