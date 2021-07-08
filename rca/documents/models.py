from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.documents.models import AbstractDocument
from wagtail.documents.models import Document as WagtailDocument


class CustomDocument(AbstractDocument):
    admin_form_fields = WagtailDocument.admin_form_fields

    # Provide help text for file field.
    # Suggested filesize (unvalidated) avoids timeout during upload.
    file = models.FileField(
        upload_to="documents",
        verbose_name=_("file"),
        help_text=_("Maximum file size: 10MB."),
    )
