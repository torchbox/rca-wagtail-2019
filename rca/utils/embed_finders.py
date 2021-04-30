from wagtail.embeds.finders.oembed import OEmbedFinder

from bs4 import BeautifulSoup


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
