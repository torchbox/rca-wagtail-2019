from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "rca.users"
    label = "users"

    def ready(self):
        from . import signals  # noqa
