from django.utils import timezone
from wagtail_personalisation.adapters import get_segment_adapter

from rca.personalisation.models import (
    CollapsibleNavigationCallToAction,
    EmbeddedFooterCallToAction,
    EventCountdownCallToAction,
    UserActionCallToAction,
)


class PersonalisedCTAMixin:
    """
    Mixin for non-Wagtail views that want to show personalised CTAs.

    Set `personalised_cta_view_type` to one of the non-page view type values
    defined in PAGE_TYPE_CHOICES (e.g. "enquire_to_study.form").
    """

    personalised_cta_view_type = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.personalised_cta_view_type or not hasattr(self.request, "session"):
            return context

        adapter = get_segment_adapter(self.request)
        adapter.refresh()
        segments = list(adapter.get_segments())

        if not segments:
            return context

        now = timezone.now()
        view_type = self.personalised_cta_view_type

        user_cta = (
            UserActionCallToAction.objects.for_view_and_segments(
                segments, now, view_type
            )
            .select_related("internal_link")
            .first()
        )
        if user_cta:
            context["personalised_user_cta"] = user_cta.get_template_data()

        footer_cta = (
            EmbeddedFooterCallToAction.objects.for_view_and_segments(
                segments, now, view_type
            )
            .select_related("internal_link")
            .first()
        )
        if footer_cta:
            context["personalised_footer_cta"] = footer_cta.get_template_data()

        countdown_cta = (
            EventCountdownCallToAction.objects.for_view_and_segments(
                segments, now, view_type
            )
            .select_related("internal_link")
            .first()
        )
        if countdown_cta:
            context["personalised_countdown_cta"] = countdown_cta.get_template_data()

        collapsible_nav = (
            CollapsibleNavigationCallToAction.objects.for_view_and_segments(
                segments, now, view_type
            ).first()
        )
        if collapsible_nav:
            context["personalised_collapsible_nav"] = (
                collapsible_nav.get_template_data()
            )

        return context
