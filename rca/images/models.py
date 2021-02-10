from django.conf import settings
from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class CustomImage(AbstractImage):
    alt = models.CharField(max_length=255, blank=True)
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


class Rendition(AbstractRendition):
    image = models.ForeignKey(
        "CustomImage", related_name="renditions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)

    def full_url(self):
        # patch for https://github.com/wagtail/wagtail/issues/6803
        url = self.url
        if url.startswith("/"):
            url = settings.BASE_URL + url
        return url
