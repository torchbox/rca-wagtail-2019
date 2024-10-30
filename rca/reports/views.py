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

    Note: There are no template overrides here, as the only change is to
    the data that is passed be exported and not the data that is displayed in the view.
    The url routing is important here, as the custom view is registered
    in the ./wagtail_hooks.py file and the index_results_url_name is required
    so that this view class is used for the report data.
    """

    index_url_name = "rca_aging_pages_report"
    index_results_url_name = "rca_aging_pages_report_results"

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
