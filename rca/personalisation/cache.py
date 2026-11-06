import hashlib
import hmac
import time

from django.conf import settings

from .state import get_personalisation_state

ANONYMOUS_CACHE_COOKIE = "__Host-rca-anonymous"
ANONYMOUS_CACHE_MAX_AGE = 3600
SHARED_PAGE_HEADER = "X-RCA-Cacheable"
SHARED_PAGE_VERSION = "public-v1"
MIN_SIGNING_KEY_BYTES = 32


def is_anonymous_cache_enabled(request):
    """Enable edge-cache markers only on the configured HTTPS host."""
    return (
        len(settings.PERSONALISATION_CACHE_SIGNING_KEY.encode())
        >= MIN_SIGNING_KEY_BYTES
        and request.get_host().lower() == settings.PERSONALISATION_CACHE_HOSTNAME
        and request.is_secure()
    )


def can_defer_personalisation(page, request):
    """Defer CTAs only for unrestricted anonymous page requests."""
    from wagtail.contrib.forms.models import FormMixin

    if (
        request.method not in ("GET", "HEAD")
        or request.user.is_authenticated
        or getattr(request, "is_preview", False)
        or isinstance(page, FormMixin)
    ):
        return False

    # Evaluate the queryset so Wagtail's later access check can reuse it.
    return not page.get_view_restrictions()


def can_share_page_response(request, *, has_personalised_ctas):
    """Require explicit deferral before allowing a page response to be shared.

    Inline personalisation touches the session even when no CTA matches.
    """
    state = get_personalisation_state(request)
    return (
        state.defer_personalisation
        and not has_personalised_ctas
        and not request.user.is_authenticated
        and not getattr(request, "is_preview", False)
        and not state.private
    )


def sign_anonymous_session(session_key, hostname, expires):
    """Bind the edge-cache marker to one session, hostname and expiry."""
    message = f"rca-anonymous-cache:v1\n{hostname}\n{session_key}\n{expires}"
    signature = hmac.new(
        settings.PERSONALISATION_CACHE_SIGNING_KEY.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"v1.{expires}.{signature}"


def set_anonymous_cache_cookie(request, response):
    max_age = min(ANONYMOUS_CACHE_MAX_AGE, request.session.get_expiry_age())
    if max_age <= 0 or not request.session.session_key:
        return
    expires = int(time.time()) + max_age
    response.set_cookie(
        ANONYMOUS_CACHE_COOKIE,
        sign_anonymous_session(
            request.session.session_key,
            settings.PERSONALISATION_CACHE_HOSTNAME,
            expires,
        ),
        max_age=max_age,
        secure=True,
        httponly=True,
        samesite="Lax",
        path="/",
    )
