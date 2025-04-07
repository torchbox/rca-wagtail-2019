from .base import *  # noqa

# SECRET_KEY is required by Django to start.
SECRET_KEY = "fake_secret_key_to_run_tests"  # pragma: allowlist secret
WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# Silence RECAPTCHA
RECAPTCHA_PUBLIC_KEY = "dummy-key-value"
RECAPTCHA_PRIVATE_KEY = "dummy-key-value"  # pragma: allowlist secret

# Don't redirect to HTTPS in tests.
SECURE_SSL_REDIRECT = False

API_CONTENT_BASE_URL = "https://rca.ac.uk"

# By default, Django uses a computationally difficult algorithm for passwords hashing.
# We don't need such a strong algorithm in tests, so use MD5
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
BIRDBATH_REQUIRED = False
CAPTCHA_TEST_MODE = True
STORAGES["staticfiles"][  # noqa
    "BACKEND"
] = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Resolve tasks immediately
# https://docs.wagtail.org/en/stable/releases/6.4.html#background-tasks-run-at-end-of-current-transaction
TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
        "ENQUEUE_ON_COMMIT": False,
    }
}
