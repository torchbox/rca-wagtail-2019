# Most of the settings are set in base.py, that's why this file appears fairly
# empty.
from .base import *  # noqa

# Explicitly disable debug mode in production
DEBUG = False

# Security configuration

# Ensure that the session cookie is only sent by browsers under an HTTPS connection.
# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True

# Ensure that the CSRF cookie is only sent by browsers under an HTTPS connection.
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True

# Don't use Birdbath in production
# https://git.torchbox.com/internal/django-birdbath#common-settings
BIRDBATH_REQUIRED = False
