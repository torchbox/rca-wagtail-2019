from django.conf import settings
from django.core.checks import Error, Tags, register

from .cache import MIN_SIGNING_KEY_BYTES


@register(Tags.security)
def check_cache_signing_key(app_configs, **kwargs):
    key = settings.PERSONALISATION_CACHE_SIGNING_KEY
    if key and len(key.encode()) < MIN_SIGNING_KEY_BYTES:
        return [
            Error(
                "PERSONALISATION_CACHE_SIGNING_KEY must contain at least "
                f"{MIN_SIGNING_KEY_BYTES} UTF-8 bytes when configured.",
                hint=(
                    "Set the same dedicated random key in Django and the Cloudflare "
                    "Worker, or leave it empty to intentionally disable caching."
                ),
                id="personalisation.E001",
            )
        ]
    return []
