from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import (
    CollapsibleNavigationCallToAction,
    EmbeddedFooterCallToAction,
    EventCountdownCallToAction,
    UserActionCallToAction,
)


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
    from wagtail.contrib.forms.models import FormMixin

    from rca.utils.models import BasePage

    if not isinstance(page, BasePage):
        return

    private = (
        request.method not in ("GET", "HEAD")
        or request.user.is_authenticated
        or getattr(request, "is_preview", False)
        or isinstance(page, FormMixin)
        or page.get_view_restrictions().exists()
    )
    request._personalisation_private = private
    # This runs before the package hooks construct their session adapter.
    request._defer_personalisation = not private


@hooks.register("construct_wagtail_userbar")
def remove_personalisation_segments(request, items):
    # Remove the personalisation segments from the wagtailuserbar that shows
    # when a Wagtail editor is logged in.
    items[:] = [item for item in items if getattr(item, "segment", None) is None]
