from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import (
    EmbeddedFooterCallToAction,
    EventCountdownCallToAction,
    UserActionCallToAction,
)


class UserActionCallToActionViewSet(SnippetViewSet):
    model = UserActionCallToAction
    icon = "snippet"
    menu_label = "User Action Pop-up CTAs"


class EmbeddedFooterCallToActionViewSet(SnippetViewSet):
    model = EmbeddedFooterCallToAction
    icon = "snippet"
    menu_label = "Embedded Footer CTAs"


class EventCountdownCallToActionViewSet(SnippetViewSet):
    model = EventCountdownCallToAction
    icon = "snippet"
    menu_label = "Event Countdown CTAs"


class PersonalisationCTAsGroup(SnippetViewSetGroup):
    menu_label = "Personalisation CTAs"
    menu_icon = "snippet"
    menu_order = 1000
    items = (
        EmbeddedFooterCallToActionViewSet,
        EventCountdownCallToActionViewSet,
        UserActionCallToActionViewSet,
    )


register_snippet(PersonalisationCTAsGroup)
