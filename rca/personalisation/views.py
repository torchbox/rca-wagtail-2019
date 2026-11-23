from importlib import import_module

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from wagtail.models import Page
from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment

from .ctas import select_ctas

# The visitor's personalisation state (visit history and segments) lives in its
# own session, whose cookie is only sent to this view. Page requests then carry
# no session cookie, so the Cloudflare Worker, which bypasses its cache for any
# request with a sessionid, still serves them from the cache.
SESSION_COOKIE_NAME = "personalisation"


def personalised_ctas(request):
    """The personalised CTAs for one page, which the page fetches once it loads.

    Pages are cached and the same for everyone, so the per-visitor work the
    page view used to do happens here instead: recording the visit (which the
    "returning user" rule reads), testing the segments' rules, and picking the
    CTAs.
    """
    page = get_object_or_404(Page.objects.live(), pk=request.GET.get("page")).specific
    # Read before the session is swapped: the logged-in user comes from the
    # site session.
    is_superuser = request.user.is_superuser

    site_session = request.session
    session_store = import_module(settings.SESSION_ENGINE).SessionStore
    request.session = session_store(request.COOKIES.get(SESSION_COOKIE_NAME))
    try:
        adapter = get_segment_adapter(request)
        adapter.add_page_visit(page)
        adapter.refresh()

        # As wagtail-personalisation's own page hook did: a superuser can
        # preview a segment with ?segment=<id> on the page, which the page
        # passes on.
        forced_segment = request.GET.get("segment")
        if is_superuser and forced_segment:
            segment = Segment.objects.filter(pk=forced_segment).first()
            if segment:
                adapter.set_segments([segment])

        context = select_ctas(list(adapter.get_segments()), page)
        personalisation_session = request.session
    finally:
        request.session = site_session

    response = TemplateResponse(request, "personalisation/ctas.html", context)
    if personalisation_session.modified:
        personalisation_session.save()
        response.set_cookie(
            SESSION_COOKIE_NAME,
            personalisation_session.session_key,
            max_age=settings.SESSION_COOKIE_AGE,
            path=reverse("personalisation_ctas"),
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=True,
            samesite="Lax",
        )
    return response
