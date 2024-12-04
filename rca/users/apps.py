from wagtail.users.apps import WagtailUsersAppConfig


class UsersConfig(WagtailUsersAppConfig):
    user_viewset = "rca.users.viewsets.UserViewSet"
