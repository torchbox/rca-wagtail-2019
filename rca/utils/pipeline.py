from django.contrib.auth.models import Group


def make_sso_users_editors(backend, user, response, *args, **kwargs):
    editors = Group.objects.get(name="Editors")
    user.groups.add(editors)
