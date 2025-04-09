import logging
import tempfile
import zipfile
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from wagtail.search import index
from wagtail.utils.text import text_from_html

from rca.utils.models import BasePage

logger = logging.getLogger(__name__)


class ShorthandStoryURLNotRecognised(ValueError):
    pass


def validate_shorthand_url(value):
    try:
        url = urlsplit(value)
    except ValueError as e:
        raise ValidationError(
            "%(value)s is not a valid URL",
            params={"value": value},
        ) from e
    if url.hostname not in settings.SHORTHAND_VALID_HOSTNAMES:
        raise ValidationError(
            (
                "%(value)s is not a supported Shorthand hostname. Speak to your website manager "
                "if you'd like to embed stories from here (it needs to be enabled in Heroku)."
            ),
            params={"value": url.hostname},
        ) from None
    if not url.path.endswith("/"):
        extra = url.path.split("/")[-1]
        raise ValidationError(
            (
                "The URL should end with a forward slash ('/'). Please remove the '%(extra)s' "
                "from the end."
            ),
            params={"extra": extra},
        )


def get_api_response(path, stream=False):
    full_path = "https://" + settings.SHORTHAND_API_DOMAIN + "/v2/" + path.lstrip("/")
    response = requests.get(
        full_path,
        stream=stream,
        headers={"Authorization": f"Token {settings.SHORTHAND_API_TOKEN}"},
    )
    response.raise_for_status()
    return response


def get_shorthand_story_id(story_url: str):
    """
    As per the [Shorthand docs](https://support.shorthand.com/en/articles/62), uses the
    `GET v2/stories/` endpoint to find the ID of the story that matches the page URL,
    (which must be set on the Shorthand side).
    """
    logger.info("Attempting to find the shorthand story ID for URL: %s", story_url)
    response = get_api_response("stories")
    for story in response.json():
        if story["url"] == story_url:
            return story["id"]
    raise ShorthandStoryURLNotRecognised(
        story_url + " cannot be matched to a Shorthand story"
    )


def get_shorthand_story_zip(story_id: str):
    """
    As per the [Shorthand docs](https://support.shorthand.com/en/articles/62), uses the
    `GET v2/stories/[STORY_ID]/?without_assets=true` endpoint to download the zip,
    streams the contents to the temporary file, and returns it.
    """
    logger.info("Downloading content for Shorthand story: %s", story_id)
    f = tempfile.NamedTemporaryFile()
    for bit in get_api_response(
        f"stories/{story_id}/?without_assets=true", stream=True
    ):
        f.write(bit)
    return f


def extract_shorthand_story_text(story_id: str):
    # Download the zip file from shorthand
    file = get_shorthand_story_zip(story_id)

    # Unzip to temporary directory
    logger.info("Extracting text from Shorthand story: %s", story_id)
    temp_dir = tempfile.mkdtemp()
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(file) as zip:
            zip.extractall(temp_dir)

        # Delete zip file
        del file

        # Extract text from index.html
        text = ""
        try:
            with open(temp_dir + "/index.html") as html:
                text += text_from_html(html.read())
        except OSError:
            pass

    non_blank_lines = [line for line in text.splitlines() if line]
    text = "\n".join(non_blank_lines)
    logger.info("The extracted text was: %s", text)
    return text


class ShorthandContentMixin(models.Model):
    shorthand_story_url = models.URLField(
        blank=True,
        validators=[validate_shorthand_url],
        verbose_name="Shorthand story URL",
        help_text=(
            "Set this to use a Shorthand story for content instead of the fields below. "
            "The value should look something like "
            "'https://royal-college-of-art.shorthandstories.com/unique-story-path/', "
            "and the 'Published URL' must be manually set to the same value under "
            "'Settings > Publishing'."
        ),
    )
    shorthand_story_id = models.CharField(max_length=15, null=True, editable=False)
    shorthand_story_text = models.TextField(editable=False)

    search_fields = BasePage.search_fields + [
        index.SearchField("shorthand_story_text"),
        index.AutocompleteField("shorthand_story_text"),
    ]

    class Meta:
        abstract = True

    def _set_shorthand_story_id(self):
        if self.shorthand_story_url:
            self.shorthand_story_id = get_shorthand_story_id(self.shorthand_story_url)
        else:
            self.shorthand_story_id = None

    def clean(self):
        """
        Overrides `Page.clean()` to apply additional validation to the 'shorthand_story_url',
        value - ensuring the story is correctly configured, so that an ID can be retreived
        from the API.
        """
        super().clean()
        try:
            self._set_shorthand_story_id()
        except ShorthandStoryURLNotRecognised as e:
            raise ValidationError(
                {
                    "shorthand_story_url": ValidationError(
                        "Wagtail cannot find a Shorthand story with the 'Published URL' "
                        f"value set to {self.shorthand_story_url}). Please update this "
                        "via the 'Settings' panel for the story, then try again."
                    )
                }
            ) from e

    def save(self, clean=True, user=None, log_action=False, **kwargs):
        """
        Overrides `Page.save()` to extract shorthand story text on save. We do this here instead of in
        `full_clean()`, because cleaning operations aren't necessary final and should really focus on
        user-managed fields that appear in the form. Also, the valud is only needed for indexing - which
        only needs to happen for saved objects.
        """
        if clean:
            self.full_clean()
        else:
            self._set_shorthand_story_id()
        if self.shorthand_story_id:
            self.shorthand_story_text = extract_shorthand_story_text(
                self.shorthand_story_id
            )
        else:
            self.shorthand_story_text = ""
        super().save(clean=False, user=user, log_action=log_action, **kwargs)

    @cached_property
    def shorthand_embed_code(self):
        if self.shorthand_story_url:
            return f'<script src="{self.shorthand_story_url}embed.js"></script>'
        return ""

    def with_content_json(self, content_json):
        """
        Overrides `Page.with_content_json()` to retain saved values for
        auto-managed fields between revisions.
        """
        obj = super().with_content_json(content_json)
        obj.shorthand_story_id = self.shorthand_story_id
        obj.shorthand_story_text = self.shorthand_story_text
        return obj

    def serializable_data(self):
        """
        Overrides `Page.serializable_data()` to keep auto-managed field values
        out of revisions.

        NOTE: Similar overrides to `get_content_json()` should prevent values
        from revisions being used for these fields; this is more a complementary
        change to avoid storing redundant data.
        """
        data = super().serializable_data()
        for field_name in ("shorthand_story_id", "shorthand_story_text"):
            data.pop(field_name, None)
        return data
