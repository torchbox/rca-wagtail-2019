import shutil
import tempfile

import requests
from django.conf import settings


class ShorthandStoryURLNotRecognised(ValueError):
    pass


def get_api_response(path, stream=False):
    full_path = "https://" + settings.SHORTHAND_API_DOMAIN + "/v2/" + path.lstrip("/")
    response = requests.get(
        full_path,
        stream=stream,
        headers={"Authorization": f"Token {settings.SHORTHAND_API_TOKEN}"},
    )
    response.raise_for_status()
    return response


def get_story_id_from_url(story_url: str):
    """
    As per the [Shorthand docs](https://support.shorthand.com/en/articles/62), uses the
    `GET v2/stories/` endpoint to find the ID of the story that matches the provided URL
    and returns it.
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


def extract_shorthand_story_text(story_url: str):
    if story_id := get_story_id_from_url(story_url):

        # Download the zip file from shorthand
        file = get_shorthand_story_zip(story_id)

        # Unzip to temporary directory
        temp_dir = tempfile.mkdtemp()
        shutil.unpack_archive(file.name, temp_dir)

        # TODO: Extract text from HTML

        # TODO: Cleanup
        del file
        del temp_dir

        return ""
    return ""
