"""
Django settings for rca project.
"""

import os
import sys

import dj_database_url

env = os.environ.copy()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Switch off DEBUG mode explicitly in the base settings.
# https://docs.djangoproject.com/en/stable/ref/settings/#debug
DEBUG = False


# Secret key is important to be kept secret. Never share it with anyone. Please
# always set it in the environment variable and never check into the
# repository.
# In its default template Django generates a 50-characters long string using
# the following function:
# https://github.com/django/django/blob/fd8a7a5313f5e223212085b2e470e43c0047e066/django/core/management/utils.py#L76-L81
# https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
if "SECRET_KEY" in env:
    SECRET_KEY = env["SECRET_KEY"]


# Define what hosts an app can be accessed by.
# It will return HTTP 400 Bad Request error if your host is not set using this
# setting.
# https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
if "ALLOWED_HOSTS" in env:
    ALLOWED_HOSTS = env["ALLOWED_HOSTS"].split(",")


# Application definition

INSTALLED_APPS = [
    # This is an app that we use for the performance monitoring.
    # You set configure it by setting the following environment variables:
    #  * SCOUT_MONITOR="True"
    #  * SCOUT_KEY="paste api key here"
    #  * SCOUT_NAME="rca"
    # https://intranet.torchbox.com/delivering-projects/tech/scoutapp/
    # According to the official docs, it's important that Scout is listed
    # first - http://help.apm.scoutapp.com/#django.
    "scout_apm.django",
    "rca.documents",
    "rca.editorial",
    "rca.events",
    "rca.forms",
    "rca.home",
    "rca.images",
    "rca.navigation",
    "rca.programmes",
    "rca.schools",
    "rca.search",
    "rca.standardpages",
    "rca.users",
    "rca.utils",
    "rca.api_content",
    "rca.shortcourses",
    "rca.guides",
    "rca.research",
    "rca.projects",
    "rca.landingpages",
    "rca.people",
    "rca.enquire_to_study",
    "rca.account_management",
    "rca.donate",
    "rca.scholarships",
    "rca.reports",
    "birdbath",
    "django_countries",
    "wagtail.contrib.settings",
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "rca.users.apps.UsersConfig",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.contrib.legacy.richtext",
    "wagtail.contrib.typed_table_block",
    "wagtail",
    "wagtailorderable",
    "import_export",
    "modelcluster",
    "taggit",
    "django_recaptcha",
    "wagtailcaptcha",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "pattern_library",
    "rca.project_styleguide.apps.ProjectStyleguideConfig",
    "rest_framework",
    "corsheaders",
    "wagtailmedia",
    "wagtail_rangefilter",
    "rangefilter",
    "wagtail_modeladmin",
    "social_django",
]

# Middleware classes
# https://docs.djangoproject.com/en/stable/ref/settings/#middleware
# https://docs.djangoproject.com/en/stable/topics/http/middleware/
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise middleware is used to server static files (CSS, JS, etc.).
    # According to the official documentation it should be listed underneath
    # SecurityMiddleware.
    # http://whitenoise.evans.io/en/stable/#quickstart-for-django-apps
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "xff.middleware.XForwardedForMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.legacy.sitemiddleware.SiteMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "rca.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                # This is a custom context processor that lets us add custom
                # global variables to all the templates.
                "rca.utils.context_processors.global_vars",
                # Social auth context_processors
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
            "builtins": ["pattern_library.loader_tags"],
        },
    }
]

WSGI_APPLICATION = "rca.wsgi.application"


# Database
# This setting will use DATABASE_URL environment variable.
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# https://github.com/kennethreitz/dj-database-url

DATABASES = {
    "default": dj_database_url.config(default="postgres:///rca", conn_max_age=600)
}


# Server-side cache settings. Do not confuse with front-end cache.
# https://docs.djangoproject.com/en/stable/topics/cache/
# If the server has a Redis instance exposed via a URL string in the REDIS_URL
# environment variable, prefer that. Otherwise use the database backend. We
# usually use Redis in production and database backend on staging and dev. In
# order to use database cache backend you need to run
# "django-admin createcachetable" to create a table for the cache.
#
# Do not use the same Redis instance for other things like Celery!

# Prefer the TLS connection URL over non
REDIS_URL = env.get("REDIS_TLS_URL", env.get("REDIS_URL"))

if REDIS_URL:
    connection_pool_kwargs = {}

    if REDIS_URL.startswith("rediss"):
        # Heroku Redis uses self-signed certificates for secure redis conections. https://stackoverflow.com/a/66286068
        # When using TLS, we need to disable certificate validation checks.
        connection_pool_kwargs["ssl_cert_reqs"] = None

    redis_options = {
        "IGNORE_EXCEPTIONS": True,
        "SOCKET_CONNECT_TIMEOUT": 2,  # seconds
        "SOCKET_TIMEOUT": 2,  # seconds
        "CONNECTION_POOL_KWARGS": connection_pool_kwargs,
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL + "/0",
            "OPTIONS": redis_options,
        },
        "renditions": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL + "/1",
            "OPTIONS": redis_options,
        },
    }
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "database_cache",
        }
    }

# Search
# https://docs.wagtail.io/en/latest/topics/search/backends.html

WAGTAILSEARCH_BACKENDS = {"default": {"BACKEND": "wagtail.search.backends.database"}}


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_I18N = True


USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

# We serve static files with Whitenoise (set in MIDDLEWARE). It also comes with
# a custom backend for the static files storage. It makes files cacheable
# (cache-control headers) for a long time and adds hashes to the file names,
# e.g. main.css -> main.1jasdiu12.css.
# The static files with this backend are generated when you run
# "django-admin collectstatic".
# http://whitenoise.evans.io/en/stable/#quickstart-for-django-apps
# https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-STORAGES
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Place static files that need a specific URL (such as robots.txt and favicon.ico) in the "public" folder
WHITENOISE_ROOT = os.path.join(BASE_DIR, "public")


# This is where Django will look for static files outside the directories of
# applications which are used by default.
# https://docs.djangoproject.com/en/stable/ref/settings/#staticfiles-dirs
STATICFILES_DIRS = [
    # "static_compiled" is a folder used by the front-end tooling
    # to output compiled static assets.
    os.path.join(PROJECT_DIR, "static_compiled")
]


# This is where Django will put files collected from application directories
# and custom direcotires set in "STATICFILES_DIRS" when
# using "django-admin collectstatic" command.
# https://docs.djangoproject.com/en/stable/ref/settings/#static-root
STATIC_ROOT = env.get("STATIC_DIR", os.path.join(BASE_DIR, "static"))


# This is the URL that will be used when serving static files, e.g.
# https://llamasavers.com/static/
# https://docs.djangoproject.com/en/stable/ref/settings/#static-url
STATIC_URL = env.get("STATIC_URL", "/static2/")


# Where in the filesystem the media (user uploaded) content is stored.
# MEDIA_ROOT is not used when S3 backend is set up.
# Probably only relevant to the local development.
# https://docs.djangoproject.com/en/stable/ref/settings/#media-root
MEDIA_ROOT = env.get("MEDIA_DIR", os.path.join(BASE_DIR, "media"))


# The URL path that media files will be accessible at. This setting won't be
# used if S3 backend is set up.
# Probably only relevant to the local development.
# https://docs.djangoproject.com/en/stable/ref/settings/#media-url
MEDIA_URL = env.get("MEDIA_URL", "/media/")


# AWS S3 buckets configuration
# This is media files storage backend configuration. S3 is our preferred file
# storage solution.
# To enable this storage backend we use django-storages package...
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
# ...that uses AWS' boto3 library.
# https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
#
# Three required environment variables are:
#  * AWS_STORAGE_BUCKET_NAME
#  * AWS_ACCESS_KEY_ID
#  * AWS_SECRET_ACCESS_KEY
# The last two are picked up by boto3:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variables
if "AWS_STORAGE_BUCKET_NAME" in env:
    # Add django-storages to the installed apps
    INSTALLED_APPS.append("storages")

    # https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-STORAGES
    STORAGES["default"]["BACKEND"] = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_STORAGE_BUCKET_NAME = env["AWS_STORAGE_BUCKET_NAME"]

    # Disables signing of the S3 objects' URLs. When set to True it
    # will append authorization querystring to each URL.
    AWS_QUERYSTRING_AUTH = False

    # Do not allow overriding files on S3 as per Wagtail docs recommendation:
    # https://docs.wagtail.io/en/stable/advanced_topics/deploying.html#cloud-storage
    # Not having this setting may have consequences in losing files.
    AWS_S3_FILE_OVERWRITE = False

    # We generally use this setting in the production to put the S3 bucket
    # behind a CDN using a custom domain, e.g. media.llamasavers.com.
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#cloudfront
    if "AWS_S3_CUSTOM_DOMAIN" in env:
        AWS_S3_CUSTOM_DOMAIN = env["AWS_S3_CUSTOM_DOMAIN"]

    # This settings lets you force using http or https protocol when generating
    # the URLs to the files. Set https as default.
    # https://github.com/jschneier/django-storages/blob/10d1929de5e0318dbd63d715db4bebc9a42257b5/storages/backends/s3boto3.py#L217
    AWS_S3_URL_PROTOCOL = env.get("AWS_S3_URL_PROTOCOL", "https:")


# Logging
# This logging is configured to be used with Sentry and console logs. Console
# logs are widely used by platforms offering Docker deployments, e.g. Heroku.
# We use Sentry to only send error logs so we're notified about errors that are
# not Python exceptions.
# We do not use default mail or file handlers because they are of no use for
# us.
# https://docs.djangoproject.com/en/stable/topics/logging/
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        # Send logs with at least INFO level to the console.
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s][%(process)d][%(levelname)s][%(name)s] %(message)s"
        }
    },
    "loggers": {
        "rca": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "wagtail": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "xff": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}


# Email settings
# We use SMTP to send emails. We typically use transactional email services
# that let us use SMTP.
# https://docs.djangoproject.com/en/2.1/topics/email/

# https://docs.djangoproject.com/en/stable/ref/settings/#email-host
if "EMAIL_HOST" in env:
    EMAIL_HOST = env["EMAIL_HOST"]

# https://docs.djangoproject.com/en/stable/ref/settings/#email-port
if "EMAIL_PORT" in env:
    try:
        EMAIL_PORT = int(env["EMAIL_PORT"])
    except ValueError:
        pass

# https://docs.djangoproject.com/en/stable/ref/settings/#email-host-user
if "EMAIL_HOST_USER" in env:
    EMAIL_HOST_USER = env["EMAIL_HOST_USER"]

# https://docs.djangoproject.com/en/stable/ref/settings/#email-host-password
if "EMAIL_HOST_PASSWORD" in env:
    EMAIL_HOST_PASSWORD = env["EMAIL_HOST_PASSWORD"]

# https://docs.djangoproject.com/en/stable/ref/settings/#email-use-tls
if env.get("EMAIL_USE_TLS", "false").lower().strip() == "true":
    EMAIL_USE_TLS = True

# https://docs.djangoproject.com/en/stable/ref/settings/#email-use-ssl
if env.get("EMAIL_USE_SSL", "false").lower().strip() == "true":
    EMAIL_USE_SSL = True

# https://docs.djangoproject.com/en/stable/ref/settings/#email-subject-prefix
if "EMAIL_SUBJECT_PREFIX" in env:
    EMAIL_SUBJECT_PREFIX = env["EMAIL_SUBJECT_PREFIX"]

# SERVER_EMAIL is used to send emails to administrators.
# https://docs.djangoproject.com/en/stable/ref/settings/#server-email
# DEFAULT_FROM_EMAIL is used as a default for any mail send from the website to
# the users.
# https://docs.djangoproject.com/en/stable/ref/settings/#default-from-email
if "SERVER_EMAIL" in env:
    SERVER_EMAIL = DEFAULT_FROM_EMAIL = env["SERVER_EMAIL"]


# Sentry configuration.
# See instructions on the intranet:
# https://intranet.torchbox.com/delivering-projects/tech/starting-new-project/#sentry
is_in_shell = len(sys.argv) > 1 and sys.argv[1] in ["shell", "shell_plus"]

if "SENTRY_DSN" in env and not is_in_shell:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.utils import get_default_release

    sentry_kwargs = {
        "dsn": env["SENTRY_DSN"],
        "integrations": [DjangoIntegration()],
    }

    # There's a chooser to toggle between environments at the top right corner on sentry.io
    # Values are typically 'staging' or 'production' but can be set to anything else if needed.
    # dokku config:set gosh SENTRY_ENVIRONMENT=staging
    # heroku config:set SENTRY_ENVIRONMENT=production
    if "SENTRY_ENVIRONMENT" in env:
        sentry_kwargs.update({"environment": env["SENTRY_ENVIRONMENT"]})

    release = get_default_release()
    if release is None:
        try:
            # But if it's not, we assume that the commit hash is available in
            # the GIT_REV environment variable. It's a default environment
            # variable used on Dokku:
            # http://dokku.viewdocs.io/dokku/deployment/methods/git/#configuring-the-git_rev-environment-variable
            release = env["GIT_REV"]
        except KeyError:
            try:
                # Assume this is a Heroku-hosted app with the "runtime-dyno-metadata" lab enabled
                release = env["HEROKU_RELEASE_VERSION"]
            except KeyError:
                # If there's no commit hash, we do not set a specific release.
                release = None

    sentry_kwargs.update({"release": release})
    sentry_sdk.init(**sentry_kwargs)

# Front-end cache
# This configuration is used to allow purging pages from cache when they are
# published.
# These settings are usually used only on the production sites.
# This is a configuration of the CDN/front-end cache that is used to cache the
# production websites.
# https://docs.wagtail.io/en/latest/reference/contrib/frontendcache.html
# You are required to set the following environment variables:
#  * FRONTEND_CACHE_CLOUDFLARE_TOKEN
#  * FRONTEND_CACHE_CLOUDFLARE_EMAIL
#  * FRONTEND_CACHE_CLOUDFLARE_ZONEID
# Can be obtained from a sysadmin.

if "FRONTEND_CACHE_CLOUDFLARE_TOKEN" in env:
    INSTALLED_APPS.append("wagtail.contrib.frontend_cache")
    WAGTAILFRONTENDCACHE = {
        "default": {
            "BACKEND": "wagtail.contrib.frontend_cache.backends.CloudflareBackend",
            "EMAIL": env["FRONTEND_CACHE_CLOUDFLARE_EMAIL"],
            "TOKEN": env["FRONTEND_CACHE_CLOUDFLARE_TOKEN"],
            "ZONEID": env["FRONTEND_CACHE_CLOUDFLARE_ZONEID"],
        }
    }


# Set s-max-age header that is used by reverse proxy/front end cache. See
# urls.py.
try:
    CACHE_CONTROL_S_MAXAGE = int(env.get("CACHE_CONTROL_S_MAXAGE", 600))
except ValueError:
    pass


# Give front-end cache 30 second to revalidate the cache to avoid hitting the
# backend. See urls.py.
CACHE_CONTROL_STALE_WHILE_REVALIDATE = int(
    env.get("CACHE_CONTROL_STALE_WHILE_REVALIDATE", 30)
)

# Required to get e.g. wagtail-sharing working on Heroku and probably many other platforms.
# https://docs.djangoproject.com/en/stable/ref/settings/#use-x-forwarded-port
USE_X_FORWARDED_PORT = env.get("USE_X_FORWARDED_PORT", "true").lower().strip() == "true"

# Security configuration
# This configuration is required to achieve good security rating.
# You can test it using https://securityheaders.com/
# https://docs.djangoproject.com/en/stable/ref/middleware/#module-django.middleware.security

# When set to True, client-side JavaScript will not to be able to access the CSRF cookie.
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True

# Force HTTPS redirect
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-ssl-redirect
if env.get("SECURE_SSL_REDIRECT", "true").strip().lower() == "true":
    SECURE_SSL_REDIRECT = True


# This will allow the cache to swallow the fact that the website is behind TLS
# and inform the Django using "X-Forwarded-Proto" HTTP header.
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# This is a setting setting HSTS header. This will enforce the visitors to use
# HTTPS for an amount of time specified in the header. Please make sure you
# consult with sysadmin before setting this.
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-hsts-seconds
if "SECURE_HSTS_SECONDS" in env:
    SECURE_HSTS_SECONDS = int(env["SECURE_HSTS_SECONDS"])


# https://docs.djangoproject.com/en/stable/ref/settings/#secure-browser-xss-filter
if env.get("SECURE_BROWSER_XSS_FILTER", "true").lower().strip() == "true":
    SECURE_BROWSER_XSS_FILTER = True


# https://docs.djangoproject.com/en/stable/ref/settings/#secure-content-type-nosniff
if env.get("SECURE_CONTENT_TYPE_NOSNIFF", "true").lower().strip() == "true":
    SECURE_CONTENT_TYPE_NOSNIFF = True


# Content Security policy settings
# http://django-csp.readthedocs.io/en/latest/configuration.html
if "CSP_DEFAULT_SRC" in env:
    MIDDLEWARE.append("csp.middleware.CSPMiddleware")

    # The “special” source values of 'self', 'unsafe-inline', 'unsafe-eval', and 'none' must be quoted!
    # e.g.: CSP_DEFAULT_SRC = "'self'" Without quotes they will not work as intended.

    CSP_DEFAULT_SRC = env.get("CSP_DEFAULT_SRC").split(",")
    if "CSP_SCRIPT_SRC" in env:
        CSP_SCRIPT_SRC = env.get("CSP_SCRIPT_SRC").split(",")
    if "CSP_STYLE_SRC" in env:
        CSP_STYLE_SRC = env.get("CSP_STYLE_SRC").split(",")
    if "CSP_IMG_SRC" in env:
        CSP_IMG_SRC = env.get("CSP_IMG_SRC").split(",")
    if "CSP_CONNECT_SRC" in env:
        CSP_CONNECT_SRC = env.get("CSP_CONNECT_SRC").split(",")
    if "CSP_FONT_SRC" in env:
        CSP_FONT_SRC = env.get("CSP_FONT_SRC").split(",")
    if "CSP_BASE_URI" in env:
        CSP_BASE_URI = env.get("CSP_BASE_URI").split(",")
    if "CSP_OBJECT_SRC" in env:
        CSP_OBJECT_SRC = env.get("CSP_OBJECT_SRC").split(",")


# Referrer-policy header settings.
# https://docs.djangoproject.com/en/stable/ref/middleware/#referrer-policy

SECURE_REFERRER_POLICY = env.get(
    "SECURE_REFERRER_POLICY", "no-referrer-when-downgrade"
).strip()

# Recaptcha
# These settings are required for the captcha challange to work.
# https://github.com/springload/wagtail-django-recaptcha

if "RECAPTCHA_PUBLIC_KEY" in env and "RECAPTCHA_PRIVATE_KEY" in env:
    NOCAPTCHA = True
    RECAPTCHA_PUBLIC_KEY = env["RECAPTCHA_PUBLIC_KEY"]
    RECAPTCHA_PRIVATE_KEY = env["RECAPTCHA_PRIVATE_KEY"]


# Django REST framework settings
# Disable basic auth to API: we have a middleware for basic auth
# that handles all requests.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    )
}

# Basic authentication settings
# These are settings to configure the third-party library:
# https://gitlab.com/tmkn/django-basic-auth-ip-whitelist
if env.get("BASIC_AUTH_ENABLED", "false").lower().strip() == "true":
    # Insert basic auth as a first middleware to be checked first, before
    # anything else.
    MIDDLEWARE.insert(0, "baipw.middleware.BasicAuthIPWhitelistMiddleware")

    # This is the credentials users will have to use to access the site.
    BASIC_AUTH_LOGIN = env.get("BASIC_AUTH_LOGIN", "rca")
    BASIC_AUTH_PASSWORD = env.get("BASIC_AUTH_PASSWORD", "showmerca")

    # This is the list of network IP addresses that are allowed in without
    # basic authentication check.
    BASIC_AUTH_WHITELISTED_IP_NETWORKS = [
        # Torchbox networks.
        # https://projects.torchbox.com/projects/sysadmin/notebook/IP%20addresses%20to%20whitelist
        "78.32.251.192/28",
        "89.197.53.244/30",
        "193.227.244.0/23",
        "2001:41c8:103::/48",
        "5.153.227.112/28",
        "193.227.244.54",
        # RCA networks
        # Kensington
        "194.80.196.128/25",
        "194.80.197.0/24",
        "194.80.198.0/24",
        # Battersea
        "194.80.196.120/29",
        "194.80.199.0/24",
        # New heroku verdant site
        "99.80.183.117",
        "99.81.135.32",
    ]

    # This is the list of hosts that website can be accessed without basic auth
    # check. This may be useful to e.g. white-list "llamasavers.com" but not
    # "llamasavers.production.torchbox.com".
    if "BASIC_AUTH_WHITELISTED_HTTP_HOSTS" in env:
        BASIC_AUTH_WHITELISTED_HTTP_HOSTS = env[
            "BASIC_AUTH_WHITELISTED_HTTP_HOSTS"
        ].split(",")

    # Change the get_client_ip function so we always get the real IP address and ignore
    # the one passed in X-Forwarded-For. This is because all requests are proxied through
    # the old site and we want to prevent direct access
    BASIC_AUTH_GET_CLIENT_IP_FUNCTION = "rca.utils.clientip.get_client_real_ip"
    BASIC_AUTH_WHITELISTED_PATHS = ["/api"]

# django-xff (https://github.com/ferrix/xff/?tab=readme-ov-file#configuration)
# --------------------------------------------------------------------------------------
XFF_TRUSTED_PROXY_DEPTH = int(env.get("XFF_TRUSTED_PROXY_DEPTH", 1))

AUTH_USER_MODEL = "users.User"

# Wagtail settings


# This name is displayed in the Wagtail admin.
WAGTAIL_SITE_NAME = "RCA Website"

# Preserve Wagtail < 2.8 behaviour
WAGTAILEMBEDS_RESPONSIVE_HTML = True

WAGTAILEMBEDS_FINDERS = [
    {"class": "wagtail.embeds.finders.oembed"},
    {"class": "rca.utils.embed_finders.CustomOEmbedFinder"},
    {"class": "rca.utils.embed_finders.WixEmbedFinder"},
    {"class": "rca.utils.embed_finders.InstagramOEmbedFinder"},
]

# This project uses it's own customised version
WAGTAIL_AGING_PAGES_ENABLED = False


# This is used by Wagtail's email notifications for constructing absolute
# URLs. Please set to the domain that users will access the admin site.
if "PRIMARY_HOST" in env:
    WAGTAILADMIN_BASE_URL = "https://{}".format(env["PRIMARY_HOST"])

# Custom image model
# https://docs.wagtail.io/en/stable/advanced_topics/images/custom_image_model.html
WAGTAILIMAGES_IMAGE_MODEL = "images.CustomImage"
WAGTAILIMAGES_FEATURE_DETECTION_ENABLED = False

# Custom image form with rights confirmation checkbox
# https://docs.wagtail.org/en/stable/reference/settings.html#wagtailimages-image-form-base
WAGTAILIMAGES_IMAGE_FORM_BASE = "rca.images.forms.RCAImageForm"

# Rich text settings to remove unneeded features
# We normally don't want editors to use the images
# in the rich text editor, for example.
# They should use the image stream block instead
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {
        "WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea",
        "OPTIONS": {"features": ["bold", "italic", "h3", "h4", "ol", "ul", "link"]},
    }
}

# Custom document model
# https://docs.wagtail.io/en/stable/advanced_topics/documents/custom_document_model.html
WAGTAILDOCS_DOCUMENT_MODEL = "documents.CustomDocument"


WAGTAIL_PASSWORD_REQUIRED_TEMPLATE = "patterns/pages/wagtail/password_required.html"


# Default size of the pagination used on the front-end.
DEFAULT_PER_PAGE = 24

# https://docs.wagtail.io/en/stable/advanced_topics/api/v2/configuration.html#wagtailapi-limit-max
WAGTAILAPI_LIMIT_MAX = 50

# https://docs.wagtail.io/en/stable/advanced_topics/api/v2/configuration.html#wagtailapi-limit-max
WAGTAILAPI_LIMIT_MAX = 50


# Styleguide
PATTERN_LIBRARY_ENABLED = env.get("PATTERN_LIBRARY_ENABLED", "false").lower() == "true"
PATTERN_LIBRARY_TEMPLATE_DIR = os.path.join(
    PROJECT_DIR, "project_styleguide", "templates"
)


# Google Tag Manager ID from env
GOOGLE_TAG_MANAGER_ID = env.get("GOOGLE_TAG_MANAGER_ID")

# Recaptcha keys from env
if "RECAPTCHA_PRIVATE_KEY" in env:
    RECAPTCHA_PRIVATE_KEY = env["RECAPTCHA_PRIVATE_KEY"]

if "RECAPTCHA_PUBLIC_KEY" in env:
    RECAPTCHA_PUBLIC_KEY = env["RECAPTCHA_PUBLIC_KEY"]
    NOCAPTCHA = True


# Variable for how long to cache content from the current api for
try:
    API_CONTENT_CACHE_TIMEOUT = int(env.get("API_CONTENT_CACHE_TIMEOUT"))
except TypeError:
    API_CONTENT_CACHE_TIMEOUT = 60 * 60 * 24

# The API url to pull content from for the homepage, see rca.api_content.content
API_CONTENT_BASE_URL = env.get("API_CONTENT_BASE_URL", "https://rca.ac.uk")

# Specifies the maximum number of fields allowed in a form submission.
# https://docs.wagtail.org/en/latest/releases/6.4.html#data-upload-max-number-fields-update
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(env.get("DATA_UPLOAD_MAX_NUMBER_FIELDS", 10_000))

CACHE_CONTROL_STALE_IF_ERROR = env.get("CACHE_CONTROL_STALE_IF_ERROR", None)

if "CSRF_TRUSTED_ORIGINS" in env:
    CSRF_TRUSTED_ORIGINS = env["CSRF_TRUSTED_ORIGINS"].split(",")
else:
    CSRF_TRUSTED_ORIGINS = ["https://www.rca.ac.uk/"]

# Enable / Disable logging exceptions for api fetches from the old site.
API_FETCH_LOGGING = env.get("API_FETCH_LOGGING", False)

# Birdbath
BIRDBATH_CHECKS = [
    "birdbath.checks.contrib.heroku.HerokuNotProductionCheck",
]
BIRDBATH_PROCESSORS = [
    "birdbath.processors.users.UserEmailAnonymiser",
    "birdbath.processors.users.UserPasswordAnonymiser",
    "birdbath.processors.contrib.wagtail.SearchQueryCleaner",
    "birdbath.processors.contrib.wagtail.FormSubmissionCleaner",
    "rca.enquire_to_study.birdbath.EnquiryFormSubmissionDeleter",
    "rca.scholarships.birdbath.ScholarshipEnquiryFormSubmissionDeleter",
    "rca.users.birdbath.StudentAccountAnonymiser",
]
BIRDBATH_REQUIRED = env.get("BIRDBATH_REQUIRED", "true").lower() == "true"
BIRDBATH_USER_ANONYMISER_EXCLUDE_SUPERUSERS = True
BIRDBATH_USER_ANONYMISER_EXCLUDE_EMAIL_RE = r"torchbox\.com$"

# Flightpath command settings
FLIGHTPATH_AUTH_KEY = os.environ.get("FLIGHTPATH_AUTH_KEY", None)
FLIGHTPATH_SOURCE_KEY = os.environ.get("FLIGHTPATH_SOURCE_KEY", None)
FLIGHTPATH_DESTINATION_KEY = os.environ.get("FLIGHTPATH_DESTINATION_KEY", None)

# Django Countries
# https://pypi.org/project/django-countries
COUNTRIES_FIRST = ["GB", "IE"]


# Global for a DO NOT REPLY email address
RCA_DNR_EMAIL = env.get("RCA_DNR_EMAIL", None)

# Needed for form field help text to use rich text.
WAGTAILFORMS_HELP_TEXT_ALLOW_HTML = True
BASIC_AUTH_DISABLE_CONSUMING_AUTHORIZATION_HEADER = True

# QS API
QS_API_ENDPOINT = env.get("QS_API_ENDPOINT", None)
QS_API_USERNAME = env.get("QS_API_USERNAME", None)
QS_API_PASSWORD = env.get("QS_API_PASSWORD", None)

# https://docs.djangoproject.com/en/3.2/ref/settings/#password-reset-timeout
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24 * 90  # 90 days, in seconds, default is 3 days

pixel_limit = env.get("WAGTAILIMAGES_MAX_IMAGE_PIXELS")
WAGTAILIMAGES_MAX_IMAGE_PIXELS = int(pixel_limit) if pixel_limit else 10000000

ALLOW_EDITORIAL_PAGE_GENERATION = (
    env.get("ALLOW_EDITORIAL_PAGE_GENERATION", "false").lower() == "true"
)
ALLOW_EVENT_PAGE_GENERATION = (
    env.get("ALLOW_EVENT_PAGE_GENERATION", "false").lower() == "true"
)

# CORS settings
if "CORS_ALLOWED_ORIGINS" in env:
    CORS_ALLOWED_ORIGINS = env["CORS_ALLOWED_ORIGINS"].split(",")
    MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

CORS_ALLOWED_ORIGIN_REGEXES = r"^/api/.*$"
CORS_ALLOW_METHODS = ["GET", "OPTIONS"]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# v2.16 WAGTAIL_SLIM_SIDEBAR https://docs.wagtail.org/en/latest/releases/2.16.html
# To avoid the following issue https://github.com/torchbox/rca-wagtail-2019/pull/866
WAGTAIL_SLIM_SIDEBAR = False


if "ENQUIRE_TO_STUDY_DESTINATION_EMAILS" in env:
    ENQUIRE_TO_STUDY_DESTINATION_EMAILS = env.get(
        "ENQUIRE_TO_STUDY_DESTINATION_EMAILS"
    ).split(",")


# Allow popups to open (can be from Paypal or other 3rd-party applications):
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

# Shorthand
# See: https://support.shorthand.com/en/articles/62
SHORTHAND_API_DOMAIN = env.get("SHORTHAND_API_DOMAIN", "api.shorthand.com")
SHORTHAND_API_TOKEN = env.get("SHORTHAND_API_TOKEN", "")
SHORTHAND_VALID_HOSTNAMES = tuple(
    host.strip()
    for host in env.get(
        "SHORTHAND_VALID_HOSTNAMES", "royal-college-of-art.shorthandstories.com"
    )
    .strip(" ,")
    .split(",")
)
# Vepple
VEPPLE_API_URL = env.get("VEPPLE_API_URL", "https://editor.rca.rvhosted.com")

# Azure AD (SSO)
AUTHENTICATION_BACKENDS = [
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

# Social Auth (SSO)
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = env.get(
    "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY", None
)
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = env.get(
    "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET", None
)
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = env.get(
    "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID", None
)
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ["username", "first_name", "last_name", "email"]
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_USER_MODEL = "users.User"
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "rca.utils.pipeline.make_sso_users_editors",
)
