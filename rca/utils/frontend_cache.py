import logging
from urllib.parse import urlsplit

import requests
from wagtail.contrib.frontend_cache.backends import (
    CloudflareBackend as WagtailCloudflareBackend,
)

logger = logging.getLogger("wagtail.frontendcache")


class CloudflareBackend(WagtailCloudflareBackend):
    def purge_prefixes(self, urls):
        """Evict a page subtree, including its cached query-string variants."""
        prefixes = sorted({urlsplit(url).netloc + urlsplit(url).path for url in urls})
        headers = {"Content-Type": "application/json"}
        if self.cloudflare_token:
            headers["Authorization"] = f"Bearer {self.cloudflare_token}"
        else:
            headers["X-Auth-Email"] = self.cloudflare_email
            headers["X-Auth-Key"] = self.cloudflare_api_key

        for start in range(0, len(prefixes), self.CHUNK_SIZE):
            end = start + self.CHUNK_SIZE
            batch = prefixes[start:end]
            try:
                response = requests.post(
                    self.cloudflare_purge_endpoint_url,
                    json={"prefixes": batch},
                    headers=headers,
                    timeout=10,
                )
                response.raise_for_status()
                if not response.json().get("success"):
                    logger.error("Cloudflare rejected cache prefix purge: %s", batch)
            except (requests.RequestException, ValueError):
                logger.exception("Could not purge Cloudflare cache prefixes: %s", batch)
