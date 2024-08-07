import zipfile
import tempfile
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from wagtail.utils.text import text_from_html


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
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(file) as zip:
        zip.extractall(temp_dir)

    # Delete zip file
    del file

    # Extract text from index.html
    text = ""
    try:
        with open(temp_dir + '/index.html') as html:
            text += text_from_html(html.read())
    except OSError:
        pass

    # Cleanup
    del temp_dir

    return text


class ShorthandContentMixin(models.Model):
    shorthand_story_url = models.URLField(
        blank=True,
        validators=[validate_shorthand_url],
        verbose_name="Shorthand story URL",
        help_text="Set this to use a Shorthand story for content instead of the fields below. The value should look something like: https://royal-college-of-art.shorthandstories.com/unique-story-path/",
    )
    shorthand_story_id = models.CharField(
        max_length=15, unique=True, null=True, editable=False
    )

    class Meta:
        abstract = True

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if self.shorthand_story_url:
            try:
                self.shorthand_story_id = get_shorthand_story_id(self.shorthand_story_url)
            except ShorthandStoryURLNotRecognised as e:
                raise ValidationError(
                    {
                        "shorthand_story_url": ValidationError(
                            (
                                "Wagtail cannot find a Shorthand story with the 'Published URL' "
                                f"value set to {self.shorthand_story_url}). Please update this "
                                "via the 'Settings' panel for the story, then try again."
                            )
                        )
                    }
                ) from e
        else:
            self.shorthand_story_id = None

    @cached_property
    def shorthand_embed_code(self):
        if self.shorthand_story_url:
            return f'<script src="{self.shorthand_story_url}/embed.js"></script>'
        return ""

    @cached_property
    def shorthand_story_text(self):
        if self.shorthand_story_id:
            return extract_shorthand_story_text(self.shorthand_story_id)
        return ""
