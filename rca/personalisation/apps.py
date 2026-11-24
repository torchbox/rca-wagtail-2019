import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PersonalisationConfig(AppConfig):
    name = "rca.personalisation"

    def ready(self):
        self._patch_origin_country_rule()
        self._stop_personalising_page_views()
        self._patch_personalisation_userbar_hook()

    def _stop_personalising_page_views(self):
        # wagtail-personalisation registers two before_serve_page hooks that
        # record the visit and refresh the visitor's segments on every page
        # view. Both write to the session, so every response set a sessionid
        # cookie and no page could be served from a shared cache. The
        # personalised_ctas view does that work instead, in its own uncached
        # request. Wagtail has no way to unregister a hook, so the two are
        # filtered out of its registry; importing the module first registers
        # them, and Wagtail's own hook discovery won't import it again.
        from wagtail import hooks
        from wagtail_personalisation import wagtail_hooks

        moved = {wagtail_hooks.set_visit_count, wagtail_hooks.segment_user}
        hooks._hooks["before_serve_page"] = [
            (fn, order)
            for fn, order in hooks._hooks.get("before_serve_page", [])
            if fn not in moved
        ]

    def _patch_origin_country_rule(self):
        # wagtail_personalisation's get_geoip_module() guards against ImportError
        # (i.e. when django.contrib.gis is not installed at all), but on Heroku
        # Django GIS *is* installed, so get_geoip_module() returns the GeoIP2
        # class successfully.  GeoIP2() then raises GeoIP2Exception at __init__
        # because GEOIP_PATH is not configured, and that exception propagates
        # uncaught, producing a 500.
        #
        # The Cloudflare header (HTTP_CF_IPCOUNTRY) is the preferred lookup path
        # and normally short-circuits before GeoIP is reached.  This patch adds a
        # safety net for requests where that header is absent (e.g. admin preview,
        # local dev): get_geoip_country returns None, causing the country rule to
        # not match rather than raising an error.
        from wagtail_personalisation.rules import OriginCountryRule

        _original = OriginCountryRule.get_geoip_country

        def get_geoip_country(self, request):
            try:
                return _original(self, request)
            except Exception as e:
                # GeoIP2Exception is raised when GEOIP_PATH is not configured.
                # We avoid importing it directly because its location within
                # django.contrib.gis.geoip2 differs between Django versions
                # (module vs package), so we match by class name instead.
                if type(e).__name__ == "GeoIP2Exception":
                    return None
                raise

        OriginCountryRule.get_geoip_country = get_geoip_country

    def _patch_personalisation_userbar_hook(self):
        # wagtail_personalisation's own construct_wagtail_userbar hook
        # (add_segment_link_items) still only accepts (request, items), and
        # its latest release (1.0.0) hasn't picked up Wagtail 8's 3-argument
        # form. Wagtail 8.1's apply_userbar_hooks() calls every registered
        # hook unconditionally as (request, items, page), with no
        # compatibility fallback for a 2-argument hook, so without this
        # patch the admin accessibility side panel raises:
        #   TypeError: add_segment_link_items() takes 2 positional
        #   arguments but 3 were given
        # Wrap the hook in place to accept and discard the extra argument.
        from wagtail import hooks

        try:
            from wagtail_personalisation import wagtail_hooks as wp_hooks

            original = wp_hooks.add_segment_link_items
        except (ImportError, AttributeError):
            logger.warning(
                "Could not import wagtail_personalisation.wagtail_hooks."
                "add_segment_link_items; skipping the Wagtail 8.1 userbar "
                "compatibility patch. Check whether wagtail-personalisation "
                "has restructured this hook and whether the patch still "
                "applies."
            )
            return

        # Hook discovery normally happens lazily on first use. Force it now
        # so the hook we want to wrap is already registered (idempotent -
        # the real, lazy discovery becomes a no-op once this has run).
        hooks.search_for_hooks()

        def add_segment_link_items(request, items, page):
            return original(request, items)

        registered = hooks._hooks.get("construct_wagtail_userbar", [])
        if not any(fn is original for fn, _order in registered):
            logger.warning(
                "wagtail_personalisation's add_segment_link_items hook was "
                "not found among the registered construct_wagtail_userbar "
                "hooks; the Wagtail 8.1 userbar compatibility patch was not "
                "applied."
            )
            return

        hooks._hooks["construct_wagtail_userbar"] = [
            (add_segment_link_items, order) if fn is original else (fn, order)
            for fn, order in registered
        ]
