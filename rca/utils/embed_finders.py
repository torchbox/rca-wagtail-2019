import re

import requests
from bs4 import BeautifulSoup
from wagtail.embeds.finders.base import EmbedFinder
from wagtail.embeds.finders.oembed import OEmbedFinder


class CustomOEmbedFinder(OEmbedFinder):
    """OEmbed finder to set video iframe titles."""

    def find_embed(self, url, max_width=None):
        embed = super().find_embed(url, max_width)
        if embed["type"] == "video":
            soup = BeautifulSoup(embed["html"], "html.parser")
            iframe = soup.find("iframe")

            # a11y: set iframe title
            try:
                iframe.attrs["title"] = embed["title"]
            except KeyError:
                pass

            embed["html"] = str(soup)

        return embed


class WixEmbedFinder(EmbedFinder):
    """Embed finder support for Wix. Wix does not have oEmbed support."""

    def accept(self, url):
        return re.match(r"^https?://(?:www\.)?embed.wix\.com/.+$", url)

    def find_embed(self, url, max_width=None):
        # Attempt to fetch the page content and scrape the title.
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.string if title_tag else None

        return {
            # Title does not support None.
            "title": title if title else "",
            "provider_name": "Wix",
            "type": "video",
            "html": '<iframe src="{url}" frameborder="0" allowfullscreen title={title}></iframe>'.format(
                url=url, title=title
            ),
            "width": 800,
            "height": 600,
        }
