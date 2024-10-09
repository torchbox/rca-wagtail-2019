from wagtail.users.views.users import UserViewSet as WagtailUserViewSet

from .forms import CustomUserEditForm


class UserViewSet(WagtailUserViewSet):
    # This replaces the WAGTAIL_USER_EDIT_FORM
    def get_form_class(self, for_update=False):
        if for_update:
            return CustomUserEditForm
        return super().get_form_class(for_update)
