import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.http.request import QueryDict
from requests.exceptions import ConnectionError, HTTPError, Timeout

"""
Static methods for adding content from the live RCA api
"""

logger = logging.getLogger(__name__)


def format_first_paragraph(input_text, tag):
    soup = BeautifulSoup(input_text, "html.parser")
    text = soup.find_all("h5")
    if text:
        return text[0].text
    else:
        text = ""
    return text


def ranged_date_format(date, date_to):
    """ Method to format dates that have 'to' and 'from' values """
    if int(date[5:7]) is int(date_to[5:7]):
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        date = datetime.strptime(date, "%Y-%m-%d")
        return date.strftime("%-d") + " - " + date_to.strftime("%-d %B %Y")
    else:
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        date = datetime.strptime(date, "%Y-%m-%d")
        return date.strftime("%-d %B") + " - " + date_to.strftime("%-d %B %Y")


class CantPullFromRcaApi(Exception):
    pass


def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Timeout:
        logger.exception(f"Timeout error occurred when fetching data from {url}")
        raise CantPullFromRcaApi(
            "Error occured when fetching further detail data from {url}"
        )
    except (HTTPError, ConnectionError):
        logger.exception(
            "HTTP/ConnectionError occured when fetching further detail data from {url}"
        )
        raise CantPullFromRcaApi(
            "Error occured when fetching further detail data from {url}"
        )
    except Exception:
        logger.exception(
            f"Exception occured when fetching further detail data from {url}"
        )
        raise CantPullFromRcaApi(
            "Error occured when fetching further detail data from {url}"
        )
    else:
        return response.json()


def parse_items_to_list(data, type):
    items = []
    if not data:
        return []
    for item in data["items"]:
        _item = {}
        if type == "News":
            detail = item["meta"]["detail_url"] + "?fields=_,date,social_image"
        if type == "Event":
            detail = item["meta"]["detail_url"] + "?fields=_,dates_times,social_image"
        if type == "alumni_stories_standard_page":
            detail = (
                item["meta"]["detail_url"]
                + "?fields=_,first_published_at,social_image,intro"
            )
        if type == "alumni_stories_blog_page":
            detail = (
                item["meta"]["detail_url"]
                + "?fields=_,first_published_at,social_image,body"
            )

        data = fetch_data(detail)
        if not data:
            return []

        if "social_image" in data and data["social_image"]:
            social_image = data["social_image"]["meta"]["detail_url"]
            social_image = requests.get(url=social_image, timeout=10)
            social_image = social_image.json()
            if "url" in social_image["rca2019_feed_image"]:
                social_image_url = social_image["rca2019_feed_image"]["url"]
                social_image_small_url = social_image["rca2019_feed_image_small"]["url"]
                _item["image"] = social_image_url
                _item["image_small"] = social_image_small_url
                _item["image_alt"] = social_image["alt"]
        date = None
        if type == "News":
            date = data["date"]
            _item["type"] = type
        if type == "Event":
            date = data["dates_times"][0]["date_from"]
            # Some events need to show 'from' and 'to' dates,
            # E.G, 7-8 January 2020
            date_to = data["dates_times"][0]["date_to"]
            if date_to:
                _item["formatted_date"] = ranged_date_format(date, date_to)
            _item["type"] = type
        if date:
            date = date[:10]  # just the year,month and day
            _item["original_date"] = date
            date = datetime.strptime(date, "%Y-%m-%d")
            date = date.strftime("%-d %B %Y")
            _item["description"] = date
        # Instead of date... alumni stories will just the body/intro text
        if type == "alumni_stories_standard_page":
            _item["description"] = data["intro"]
            _item["type"] = "Alumni story"
            date = data["meta"]["first_published_at"]
        if type == "alumni_stories_blog_page":
            _item["description"] = format_first_paragraph(data["body"], "h5")
            _item["type"] = "Alumni story"
            date = data["meta"]["first_published_at"]

        _item["title"] = item["title"]
        _item["link"] = item["meta"]["html_url"]
        items.append(_item)

    return items


def pull_news_and_events(programme_type_slug=None):
    # 'News' is actually a mixture of NewItem and RcaBlogPage models.
    # So pull 3 of both from the API and order them by the date field.
    # Then select how many we need depending on the events content.

    # First get the Events
    query = QueryDict(mutable=True)
    query.update(
        {
            "type": "rca.EventItem",
            "limit": 1,
            "event_date_from": True,
            "show_on_homepage": "true",
        }
    )

    if programme_type_slug:
        query.update({"rp": programme_type_slug})

    query = query.urlencode()
    events_url = f"{settings.API_CONTENT_BASE_URL}/api/v2/pages/?{query}"

    # By default, work with 3 news items but if we pull events, get 2
    # so we end up with 2 x News/Blog and 1 x Event.
    news_items_to_get = 3

    events_data = []
    fetched_event_data = fetch_data(events_url)
    if (
        fetched_event_data
        and "total_count" in fetched_event_data["meta"]
        and fetched_event_data["meta"]["total_count"] > 0
    ):
        news_items_to_get = 2
        events_data = parse_items_to_list(fetched_event_data, "Event")

    # News and Blogs
    # Pull 3 Blog items
    query = QueryDict(mutable=True)
    query.update(
        {
            "limit": "3",
            "order": "-date",
            "type": "rca.RcaBlogPage",
            "show_on_homepage": "true",
            "tags_not": "Alumni_Story",
        }
    )
    if programme_type_slug:
        query.update({"rp": programme_type_slug})

    query = query.urlencode()
    blog_url = f"{settings.API_CONTENT_BASE_URL}/api/v2/pages/?{query}"
    fetched_blog_data = fetch_data(blog_url)
    # Blog and News are both being used for News content, so they can
    # both go to the parser as 'News'.
    blog_data = parse_items_to_list(fetched_blog_data, "News")

    # Pull 3 News items
    query = QueryDict(mutable=True)
    query.update(
        {
            "limit": 3,
            "order": "-date",
            "type": "rca.NewsItem",
            "show_on_homepage": "true",
        }
    )
    if programme_type_slug:
        query.update({"rp": programme_type_slug})
    query = query.urlencode()
    news_url = f"{settings.API_CONTENT_BASE_URL}/api/v2/pages/?{query}"
    news_data = []

    fetched_news_data = fetch_data(news_url)
    news_data = parse_items_to_list(fetched_news_data, "News")

    news_and_blog_data = news_data + blog_data
    # Sort by the date
    news_and_blog_data.sort(key=lambda x: x["original_date"])
    news_and_blog_data.reverse()
    # Slice for how many items we want to get depending on the Events pulled.
    news_and_blog_data = news_and_blog_data[:news_items_to_get]

    return news_and_blog_data + events_data


def pull_alumni_stories(programme_type_slug=None):
    # 'Alumni stories' are a mixture of StandardPage and RcaBlogPage models.
    # that are tagged with 'alumni-stories...

    # Pull 3 StandardPage items
    query = QueryDict(mutable=True)
    query.update(
        {
            "limit": 3,
            "order": "-first_published_at",
            "type": "rca.StandardPage",
            "tags": "Alumni_Story",
            "show_on_homepage": "true",
        }
    )
    alumni_stories_standard_page_data = []
    if programme_type_slug:
        query.update({"rp": programme_type_slug})
    query = query.urlencode()
    url = f"{settings.API_CONTENT_BASE_URL}/api/v2/pages/?{query}"

    fetched_alumni_stories_data = fetch_data(url)
    alumni_stories_standard_page_data = parse_items_to_list(
        fetched_alumni_stories_data, "alumni_stories_standard_page_data"
    )

    # Pull 3 BlogPage items
    query = QueryDict(mutable=True)
    query.update(
        {
            "limit": 3,
            "order": "-first_published_at",
            "type": "rca.RcaBlogPage",
            "tags": "Alumni_Story",
            "show_on_homepage": "true",
        }
    )
    if programme_type_slug:
        query.update({"rp": programme_type_slug})
    query = query.urlencode()
    url = f"{settings.API_CONTENT_BASE_URL}/api/v2/pages/?{query}"

    fetched_blog_data = fetch_data(url)
    alumni_stories_blog_page_data = parse_items_to_list(
        fetched_blog_data, "alumni_stories_blog_page"
    )

    alumni_stories_data = (
        alumni_stories_blog_page_data + alumni_stories_standard_page_data
    )
    return alumni_stories_data
