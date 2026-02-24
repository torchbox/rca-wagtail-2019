# This module provides a custom IP resolution function for wagtail_personalisation.
#
# The default wagtail_personalisation behaviour uses Django's GeoIP2 backend to
# resolve a client IP address to a country. That requires a local MaxMind GeoIP
# database file (GeoLite2-City.mmdb / GeoLite2-Country.mmdb) to be present and
# configured via GEOIP_PATH. When the database is absent, any page that uses an
# OriginCountryRule or OriginContinentRule personalisation rule raises an
# exception rather than gracefully skipping the rule.
#
# This site is served behind Cloudflare, which performs its own geo-lookup and
# injects the client's real IP via the CF-Connecting-IP header. By pointing
# WAGTAIL_PERSONALISATION_IP_FUNCTION at get_client_ip below, we supply the
# real client IP ourselves from the Cloudflare header. If the header is absent
# (e.g. in local development or when not behind Cloudflare), the KeyError
# propagates, which is intentional – it surfaces misconfiguration rather than
# silently skipping personalisation.


def get_client_ip(request):
    # Read the client IP forwarded by Cloudflare rather than relying on
    # REMOTE_ADDR, which would be the Cloudflare edge node's address.
    return request["HTTP_CF_CONNECTING_IP"]
