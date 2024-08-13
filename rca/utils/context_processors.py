from django.conf import settings


def global_vars(request):
    return {
        "GOOGLE_TAG_MANAGER_ID": getattr(settings, "GOOGLE_TAG_MANAGER_ID", None),
        "CANONICAL_HOST": (
            ("https://" if request.is_secure() else "http://") + request.get_host()
        ),
    }
