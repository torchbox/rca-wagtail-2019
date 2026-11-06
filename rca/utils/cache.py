from urllib.parse import urlsplit

from django.conf import settings
from django.urls import reverse
from django.views.decorators.cache import cache_control
from wagtail.contrib.frontend_cache.utils import (
    get_backends,
    purge_pages_from_cache,
    purge_url_from_cache,
)
from wagtail.models import Site

from .frontend_cache import CloudflareBackend


def purge_page_restriction_cache(page):
    backends = get_backends()
    if not backends:
        return

    urls = []
    for site in Site.objects.select_related("root_page"):
        root_path = site.root_page.url_path
        if page.url_path.startswith(root_path):
            relative_path = page.url_path.removeprefix(root_path)
            path = reverse("wagtail_serve", args=[relative_path])
        elif root_path.startswith(page.url_path):
            # A restriction above a site root applies to that entire site.
            path = reverse("wagtail_serve", args=[""])
        else:
            continue
        urls.append(site.root_url + path)

    for name, backend in backends.items():
        if isinstance(backend, CloudflareBackend):
            backend.purge_prefixes(
                [
                    url
                    for url in urls
                    if backend.invalidates_hostname(urlsplit(url).netloc)
                ]
            )
        else:
            purge_pages_from_cache(
                page.get_descendants(inclusive=True), backends=[name]
            )


def purge_cache_on_all_sites(path):
    if settings.DEBUG:
        return

    for site in Site.objects.all():
        purge_url_from_cache("{}{}".format(site.root_url.rstrip("/"), path))


def get_default_cache_control_kwargs():
    """
    Get cache control parameters used by the cache control decorators
    used by default on most pages. These parameters are meant to be
    sane defaults that can be applied to a standard content page.
    """
    s_maxage = getattr(settings, "CACHE_CONTROL_S_MAXAGE", None)
    stale_while_revalidate = getattr(
        settings, "CACHE_CONTROL_STALE_WHILE_REVALIDATE", None
    )
    cache_control_kwargs = {
        "s_maxage": s_maxage,
        "stale_while_revalidate": stale_while_revalidate,
        "public": True,
    }
    return {k: v for k, v in cache_control_kwargs.items() if v is not None}


def get_default_cache_control_decorator():
    """
    Get cache control decorator that can be applied to views as a
    sane default for normal content pages.
    """
    cache_control_kwargs = get_default_cache_control_kwargs()
    return cache_control(**cache_control_kwargs)
