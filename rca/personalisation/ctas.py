"""Which personalised CTAs a visitor sees on a page."""

from django.utils import timezone

from .models import (
    CollapsibleNavigationCallToAction,
    EmbeddedFooterCallToAction,
    EventCountdownCallToAction,
    UserActionCallToAction,
)


def select_ctas(segments, page):
    """The CTAs for ``page`` and the visitor's ``segments``, keyed by template name.

    One of each CTA type at most, so a visitor never sees two of the same kind.
    """
    if not segments:
        return {}

    now = timezone.now()
    ctas = {}

    user_cta = (
        UserActionCallToAction.objects.for_page_and_segments(segments, now, page)
        .select_related("internal_link")
        .first()
    )
    if user_cta:
        ctas["personalised_user_cta"] = user_cta.get_template_data()

    footer_cta = (
        EmbeddedFooterCallToAction.objects.for_page_and_segments(segments, now, page)
        .select_related("internal_link")
        .first()
    )
    if footer_cta:
        ctas["personalised_footer_cta"] = footer_cta.get_template_data()

    countdown_cta = (
        EventCountdownCallToAction.objects.for_page_and_segments(segments, now, page)
        .select_related("internal_link")
        .first()
    )
    if countdown_cta:
        ctas["personalised_countdown_cta"] = countdown_cta.get_template_data()

    collapsible_nav = CollapsibleNavigationCallToAction.objects.for_page_and_segments(
        segments, now, page
    ).first()
    if collapsible_nav:
        ctas["personalised_collapsible_nav"] = collapsible_nav.get_template_data()

    return ctas
