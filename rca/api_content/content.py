import logging
from datetime import datetime

import requests
from django.http.request import QueryDict

"""
Static methods for adding content from the live RCA api
"""

logger = logging.getLogger(__name__)


class CantPullFromRcaApi(Exception):
    pass


def parse_items_to_list(data, type):
    items = []

    for item in data["items"]:
        _item = {}
        if type == "News":
            detail = item["meta"]["detail_url"] + "?fields=_,date,feed_image"
        if type == "Event":
            detail = item["meta"]["detail_url"] + "?fields=_,dates_times,feed_image"
        if type == "Alumni stories":
            detail = item["meta"]["detail_url"] + "?fields=_,feed_image,intro"

        try:
            response = requests.get(url=detail)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            error_text = "Error occured when fetching further detail data"
            logger.exception(error_text)
            raise CantPullFromRcaApi(error_text)

        data = response.json()
        if "feed_image" in data:
            feed_image = data["feed_image"]["meta"]["detail_url"]
            feed_image = requests.get(url=feed_image)
            feed_image = feed_image.json()
            feed_image_url = feed_image["rca2019_feed_image"]["url"]
            feed_image_small_url = feed_image["rca2019_feed_image_small"]["url"]
            _item["image"] = feed_image_url
            _item["image_small"] = feed_image_small_url
            _item["image_alt"] = feed_image["alt"]
        date = False
        if type == "News":
            date = data["date"]
        if type == "Event":
            date = data["dates_times"][0]["date_from"]
        if type == "Alumni stories":
            _item["description"] = data["intro"]
        if date:
            date = datetime.strptime(date, "%Y-%m-%d")
            date = date.strftime("%-d %B %Y")
            _item["description"] = date

        _item["title"] = item["title"]
        _item["type"] = type
        _item["link"] = item["meta"]["html_url"]
        items.append(_item)

    return items


def pull_news_and_events(programme_type_slug=None):
    # Get the latest 2 news items and 1 event item tagged
    # with the programme type taxonomy, if there are no events, use 3 news
    query = QueryDict(mutable=True)
    query.update({"limit": 1, "event_date_from": True, "type": "rca.EventItem"})

    if programme_type_slug:
        query.update({"rp": programme_type_slug})

    query = query.urlencode()
    events_url = f"https://rca.ac.uk/api/v2/pages/?{query}"

    # By default, get 3 news items but if we pull events, get 2
    news_items_to_get = 3

    # First get the events
    events_data = []
    try:
        response = requests.get(url=events_url)
        response.raise_for_status()
        logger.info("pulling Events from API")
    except requests.exceptions.HTTPError:
        error_text = "Error occured when fetching event data"
        logger.exception(error_text)
        raise CantPullFromRcaApi(error_text)
    else:
        data = response.json()

        if data["meta"]["total_count"] > 0:
            news_items_to_get = 2
            events_data = parse_items_to_list(data, "Event")

    # News
    query = QueryDict(mutable=True)
    query.update({"limit": news_items_to_get, "order": "-date", "type": "rca.NewsItem"})
    if programme_type_slug:
        query.update({"rp": programme_type_slug})
    query = query.urlencode()
    news_url = f"https://rca.ac.uk/api/v2/pages/?{query}"
    news_data = []

    try:
        response = requests.get(url=news_url)
        response.raise_for_status()
        logger.info("Pulling News from API")
    except requests.exceptions.HTTPError:
        error_text = "Error occured when fetching News data"
        logger.exception(error_text)
        raise CantPullFromRcaApi(error_text)
    else:
        data = response.json()
        news_data = parse_items_to_list(data, "News")

    return news_data + events_data


def pull_alumni_stories(programme_type_slug=None):

    query = QueryDict(mutable=True)
    query.update(
        {
            "limit": 3,
            "order": "-first_published_at",
            "type": "rca.StandardPage",
            "tags": "alumni-story",
        }
    )
    if programme_type_slug:
        query.update({"rp": programme_type_slug})
    query = query.urlencode()
    url = f"https://rca.ac.uk/api/v2/pages/?{query}"

    try:
        response = requests.get(url=url)
        response.raise_for_status()
        logger.info("pulling Alumni Stories from API")
    except requests.exceptions.HTTPError:
        error_text = "Error occured when fetching alumni stories data"
        logger.exception(error_text)
        raise CantPullFromRcaApi(error_text)
    else:
        data = response.json()
        # Should this parse also be in a better try/catch?
        alumni_stories_data = parse_items_to_list(data, "Alumni stories")
        return alumni_stories_data
