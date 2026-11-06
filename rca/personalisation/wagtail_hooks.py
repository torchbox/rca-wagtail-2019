from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .cache import can_defer_personalisation
from .models import (
    CollapsibleNavigationCallToAction,
    EmbeddedFooterCallToAction,
    EventCountdownCallToAction,
    UserActionCallToAction,
)
from .state import get_personalisation_state


class CollapsibleNavigationCallToActionViewSet(SnippetViewSet):
    model = CollapsibleNavigationCallToAction
    icon = "snippet"
    menu_label = "Collapsible Navigation CTAs"


class EmbeddedFooterCallToActionViewSet(SnippetViewSet):
    model = EmbeddedFooterCallToAction
    icon = "snippet"
    menu_label = "Embedded Footer CTAs"


class EventCountdownCallToActionViewSet(SnippetViewSet):
    model = EventCountdownCallToAction
    icon = "snippet"
    menu_label = "Event Countdown CTAs"


class UserActionCallToActionViewSet(SnippetViewSet):
    model = UserActionCallToAction
    icon = "snippet"
    menu_label = "User Action Pop-up CTAs"


class PersonalisationCTAsGroup(SnippetViewSetGroup):
    menu_label = "Personalisation CTAs"
    menu_icon = "snippet"
    menu_order = 1000
    items = (
        CollapsibleNavigationCallToActionViewSet,
        EmbeddedFooterCallToActionViewSet,
        EventCountdownCallToActionViewSet,
        UserActionCallToActionViewSet,
    )


register_snippet(PersonalisationCTAsGroup)


@hooks.register("before_serve_page", order=-1)
def defer_anonymous_personalisation(page, request, serve_args, serve_kwargs):
    """Set deferral before upstream hooks can touch the visitor's session.

    Fragment access is checked separately by personalisation_ctas.
    """
    from rca.utils.models import BasePage

    if not isinstance(page, BasePage):
        return

    deferred = can_defer_personalisation(page, request)
    state = get_personalisation_state(request)
    state.defer_personalisation = deferred
    state.private = not deferred


@hooks.register("construct_wagtail_userbar")
def remove_personalisation_segments(request, items):
    # Remove the personalisation segments from the wagtailuserbar that shows
    # when a Wagtail editor is logged in.
    items[:] = [item for item in items if getattr(item, "segment", None) is None]
