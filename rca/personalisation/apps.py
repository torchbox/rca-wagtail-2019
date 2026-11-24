from django.apps import AppConfig


class PersonalisationConfig(AppConfig):
    name = "rca.personalisation"

    def ready(self):
        self._patch_origin_country_rule()
        self._stop_personalising_page_views()

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
