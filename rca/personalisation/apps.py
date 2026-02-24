from django.apps import AppConfig


class PersonalisationConfig(AppConfig):
    name = "rca.personalisation"

    def ready(self):
        self._patch_origin_country_rule()

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
