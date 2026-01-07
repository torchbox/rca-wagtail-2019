from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import (
    CollapsibleNavigationCallToAction,
    EmbeddedFooterCallToAction,
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


class CollapsibleNavigationCallToActionViewSet(SnippetViewSet):
    model = CollapsibleNavigationCallToAction
    icon = "snippet"
    menu_label = "Collapsible Navigation CTAs"


class PersonalisationCTAsGroup(SnippetViewSetGroup):
    menu_label = "Personalisation CTAs"
    menu_icon = "snippet"
    menu_order = 1000
    items = (
        CollapsibleNavigationCallToActionViewSet,
        EmbeddedFooterCallToActionViewSet,
        UserActionCallToActionViewSet,
    )


register_snippet(PersonalisationCTAsGroup)
