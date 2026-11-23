from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from wagtail.models import Page
from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment

from .ctas import select_ctas


def personalised_ctas(request):
    """The personalised CTAs for one page, which the page fetches once it loads.

    Pages are cached and the same for everyone, so the per-visitor work the
    page view used to do happens here instead: recording the visit (which the
    "returning user" rule reads), testing the segments' rules, and picking the
    CTAs. This is the only request that touches the visitor's session.
    """
    page = get_object_or_404(Page.objects.live(), pk=request.GET.get("page")).specific

    adapter = get_segment_adapter(request)
    adapter.add_page_visit(page)
    adapter.refresh()

    # As wagtail-personalisation's own page hook did: a superuser can preview
    # a segment with ?segment=<id> on the page, which the page passes on.
    forced_segment = request.GET.get("segment")
    if request.user.is_superuser and forced_segment:
        segment = Segment.objects.filter(pk=forced_segment).first()
        if segment:
            adapter.set_segments([segment])

    return TemplateResponse(
        request,
        "personalisation/ctas.html",
        select_ctas(list(adapter.get_segments()), page),
    )
