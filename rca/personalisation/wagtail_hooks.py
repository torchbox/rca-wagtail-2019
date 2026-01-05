from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import UserActionCallToAction


class UserActionCallToActionViewSet(SnippetViewSet):
    model = UserActionCallToAction
    icon = "snippet"
    menu_label = "User Action Pop-up CTAs"


class PersonalisationCTAsGroup(SnippetViewSetGroup):
    menu_label = "Personalisation CTAs"
    menu_icon = "snippet"
    menu_order = 1000
    items = (UserActionCallToActionViewSet,)


register_snippet(PersonalisationCTAsGroup)
