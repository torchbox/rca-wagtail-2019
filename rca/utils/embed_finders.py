import re

import requests
from bs4 import BeautifulSoup
from wagtail.embeds.exceptions import EmbedNotFoundException
from wagtail.embeds.finders.base import EmbedFinder
from wagtail.embeds.finders.oembed import OEmbedFinder


class InstagramOEmbedFinder(EmbedFinder):
    """Embed finder support for Instagram using simple iframe approach."""

    def accept(self, url):
        return re.match(
            r"^https?://(?:www\.)?instagram\.com/(?:[^/]+/)?(?:p|tv|reel)/.+$", url
        )

    def find_embed(self, url, max_width=None):
        # Extract the post ID from the URL - support both with and without username
        match = re.search(r"instagram\.com/(?:[^/]+/)?(?:p|tv|reel)/([^/?]+)", url)
        if not match:
            raise EmbedNotFoundException

        post_id = match.group(1)

        html = f'<iframe src="https://www.instagram.com/p/{post_id}/embed/" frameborder="0" scrolling="no" allowtransparency="true"></iframe>'  # noqa: E501

        return {
            "title": f"Instagram Post {post_id}",
            "provider_name": "Instagram",
            "type": "rich",
            "html": html,
            "width": 400,
            "height": 700,
        }


class CustomOEmbedFinder(OEmbedFinder):
    """OEmbed finder to set video iframe titles."""

    def __init__(self, **options):
        # Add TikTok as an additional provider
        additional_providers = [
            {
                "endpoint": "https://www.tiktok.com/oembed",
                "urls": [
                    r"^https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+.*$",
                    r"^https?://(?:www\.)?tiktok\.com/@[\w.-]+/photo/\d+.*$",
                    r"^https?://vm\.tiktok\.com/[\w-]+/?$",
                    r"^https?://(?:www\.)?tiktok\.com/t/[\w-]+/?$",
                ],
            }
        ]

        super().__init__(providers=additional_providers, **options)

    def find_embed(self, url, max_width=None):
        # Convert TikTok photo URLs to video URLs for oEmbed API
        if "tiktok.com" in url:
            # Use regex to dynamically convert photo URLs to video URLs
            url = re.sub(r"/photo/", "/video/", url)

        embed = super().find_embed(url, max_width)
        if embed["type"] == "video":
            soup = BeautifulSoup(embed["html"], "html.parser")
            iframe = soup.find("iframe")

            # a11y: set iframe title
            if iframe:
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
