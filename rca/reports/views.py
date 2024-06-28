from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from wagtail.admin.views.reports.aging_pages import (
    AgingPagesView as OriginalAgingPagesView,
)
from wagtail.coreutils import multigetattr


class AgingPagesReportView(OriginalAgingPagesView):
    """
    A customised version of Wagtail's built-in report, which includes
    page's full URL as a column when the data is exported.
    """

    list_export = [
        "title",
        "get_full_url",
        "status_string",
        "last_published_at",
        "last_published_by_user",
        "content_type",
    ]

    export_headings = {
        "get_full_url": _("URL"),
        **OriginalAgingPagesView.export_headings,
    }

    def to_row_dict(self, item):
        """
        Overrides `wagtail.admin.views.mixins.SpreadsheetExportMixin.to_row_dict()`
        to call the 'get_full_url()' method when it comes across it - passing along
        the current `HttpRequest` to allow sharing of 'site root path' data,
        vastly reducing the number of database queries.
        """
        row_dict = {}
        for fieldname in self.list_export:
            if fieldname == "get_full_url":
                row_dict[fieldname] = item.specific_deferred.get_full_url(self.request)
            else:
                row_dict[fieldname] = multigetattr(item, fieldname)
        return OrderedDict(row_dict)
