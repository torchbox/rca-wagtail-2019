from unittest.mock import patch

from bs4 import BeautifulSoup
from django.test import TestCase

from rca.utils.embed_finders import CustomOEmbedFinder


@patch("rca.utils.embed_finders.OEmbedFinder.find_embed")
class CustomOEmbedFinderTest(TestCase):
    def test_video_iframe_title_is_set(self, mock_find_embed):
        mock_find_embed.return_value = {
            "html": '<iframe src="www.example.com"></iframe>',
            "type": "video",
            "title": "Some video",
        }

        finder = CustomOEmbedFinder()
        result = finder.find_embed("www.example.com")
        soup = BeautifulSoup(result["html"], "html.parser")
        self.assertEqual(soup.find("iframe").attrs.get("title"), "Some video")

    def test_nonvideo_iframe_title_is_not_set(self, mock_find_embed):
        mock_find_embed.return_value = {
            "html": '<iframe src="www.example.com"></iframe>',
            "type": "not a video",
            "title": "Not a video",
        }

        finder = CustomOEmbedFinder()
        result = finder.find_embed("www.example.com")
        soup = BeautifulSoup(result["html"], "html.parser")
        self.assertEqual(soup.find("iframe").attrs.get("title"), None)

    def test_video_output_html(self, mock_find_embed):
        mock_find_embed.return_value = {
            "html": '<iframe src="www.example.com"></iframe>',
            "type": "video",
            "title": "Some video",
        }

        finder = CustomOEmbedFinder()
        result = finder.find_embed("www.example.com")
        self.assertEqual(
            result["html"],
            '<iframe src="www.example.com" title="Some video"></iframe>',
        )

    def test_nonvideo_output_html(self, mock_find_embed):
        mock_find_embed.return_value = {
            "html": '<iframe src="www.example.com"></iframe>',
            "type": "not a video",
            "title": "Something else",
        }

        finder = CustomOEmbedFinder()
        result = finder.find_embed("www.example.com")
        self.assertEqual(
            result["html"],
            '<iframe src="www.example.com"></iframe>',
        )

    def test_tiktok_url_acceptance(self, mock_find_embed):
        """Test that CustomOEmbedFinder now handles TikTok URLs."""
        mock_find_embed.return_value = {
            "html": '<iframe src="https://www.tiktok.com/embed/1234567890123456789"></iframe>',
            "type": "video",
            "title": "TikTok video",
        }
        finder = CustomOEmbedFinder()

        # Test various TikTok URL formats
        test_urls = [
            "https://www.tiktok.com/@username/video/1234567890123456789",
            "https://vm.tiktok.com/ZMxxxxxx/",
            "https://www.tiktok.com/t/ZMxxxxxx/",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                self.assertTrue(finder.accept(url))
