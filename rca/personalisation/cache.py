import hashlib
import hmac
import time

from django.conf import settings

ANONYMOUS_CACHE_COOKIE = "__Host-rca-anonymous"
ANONYMOUS_CACHE_MAX_AGE = 3600
SHARED_PAGE_HEADER = "X-RCA-Cacheable"
SHARED_PAGE_VERSION = "public-v1"


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
