import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache
from django.http.request import QueryDict
from requests.exceptions import ConnectionError, HTTPError, Timeout

"""
Static methods for adding content from the live RCA api
"""

logger = logging.getLogger(__name__)


class CantPullFromRcaApi(Exception):
    pass


def format_first_paragraph(input_text, tag):
    soup = BeautifulSoup(input_text, "html.parser")
    text = soup.find_all("h5")
    if text:
        return text[0].text
    else:
        text = ""
    return text


def ranged_date_format(date, date_to):
    """Method to format dates that have 'to' and 'from' values"""
    date = datetime.strptime(date, "%Y-%m-%d")
    date_to = datetime.strptime(date_to, "%Y-%m-%d")

    if date.year == date_to.year:
        if date.month == date_to.month:
            return date.strftime("%-d") + "–" + date_to.strftime("%-d %B %Y")
        else:
            return date.strftime("%-d %B") + " – " + date_to.strftime("%-d %B %Y")
    else:
        return date.strftime("%-d %B %Y") + " – " + date_to.strftime("%-d %B %Y")


def fetch_data(url, **params):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except Timeout:
        if settings.API_FETCH_LOGGING:
            logger.exception(f"Timeout error occurred when fetching data from {url}")
        raise CantPullFromRcaApi(
            f"Error occured when fetching further detail data from {url}"
        )
    except (HTTPError, ConnectionError):
        if settings.API_FETCH_LOGGING:
            logger.exception(
                f"HTTP/ConnectionError occured when fetching further detail data from {url}"
            )
        raise CantPullFromRcaApi(
            f"Error occured when fetching further detail data from {url}"
        )
    except Exception:
        if settings.API_FETCH_LOGGING:
            logger.exception(
                f"Exception occured when fetching further detail data from {url}"
            )
        raise CantPullFromRcaApi(
            f"Error occured when fetching further detail data from {url}"
        )
    else:
        return response.json()


def parse_items_to_list(data, type):
    items = []
    detail = ""
    if not data:
        return []
    for item in data["items"]:
        _item = {}
        if type == "Event":
            detail = item["meta"]["detail_url"] + "?fields=_,dates_times,social_image"
        elif type == "News":
            detail = item["meta"]["detail_url"] + "?fields=_,date,social_image"
        elif type == "alumni_stories_blog_page":
            detail = (
                item["meta"]["detail_url"]
                + "?fields=_,first_published_at,social_image,body"
            )

        elif type == "alumni_stories_standard_page":
            detail = (
                item["meta"]["detail_url"]
                + "?fields=_,first_published_at,social_image,intro"
            )
        if not detail:
            return []
        data = fetch_data(detail)
        if not data:
            return []

        if "social_image" in data and data["social_image"]:
            social_image = data["social_image"]["meta"]["detail_url"]
            social_image = fetch_data(url=social_image)
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
    # 'News' is actually a mixture of NewsItem and RcaBlogPage models.
    # So pull 3 of both from the API and order them by the date field.
    # Then select how many we need depending on the events content.
    NEWS_ITEMS = 3
    # By default, work with 3 news items but if we pull events, get 2
    # so we end up with 2 x News/Blog and 1 x Event.

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

    events_data = []
    fetched_event_data = fetch_data(events_url)
    if (
        fetched_event_data
        and "total_count" in fetched_event_data["meta"]
        and fetched_event_data["meta"]["total_count"] > 0
    ):
        NEWS_ITEMS = 2
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
    news_and_blog_data = news_and_blog_data[:NEWS_ITEMS]

    return news_and_blog_data + events_data


def pull_tagged_news_and_events(*tags):
    """
    Return a list of items matching the provided tags.

    By default, include 1 article followed by 2 events (when available)
    If there is only 1 event, include 2 articles (or as many as are available), followed by the event
    If there are no matching events, include 3 articles (or as many as are available).
    If there are no matching articles, show 3 events (or as many as are available).
    """
    api_url = f"{settings.API_CONTENT_BASE_URL}/api/v2/pages/"

    if not tags:
        return []

    tags_string = ",".join(tags)
    # Fetch Events
    articles_required = 1
    result = fetch_data(
        api_url, type="rca.EventItem", limit=3, event_date_from=True, tags=tags_string
    )
    events = parse_items_to_list(result, "Event")
    if len(events) < 2:
        # fetch more articles to fill the empty slots
        articles_required = 3 - len(events)

    # Fetch Blog items
    result = fetch_data(
        api_url,
        type="rca.RcaBlogPage",
        limit=articles_required,
        order="-date",
        tags=tags_string,
        tags_not="Alumni_Story",
    )
    # Blog and News are both being used for News content, so they can
    # both go to the parser as 'News'.
    blogs = parse_items_to_list(result, "News")

    # Fetch News items
    result = fetch_data(
        api_url,
        type="rca.NewsItem",
        limit=articles_required,
        order="-date",
        tags=tags_string,
        tags_not="Alumni_Story",
    )
    news = parse_items_to_list(result, "News")

    # Combine Blog and News results
    articles = news + blogs

    # Return only events if there are no articles
    if not articles:
        return events

    # Order combined articles by latest first
    articles.sort(key=lambda x: x["original_date"], reverse=True)
    # Return a mix of articles and events
    return articles[:articles_required] + events[:2]


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

    return alumni_stories_blog_page_data + alumni_stories_standard_page_data


class _BaseContentAPI:
    def __init__(self, func, cache_key):
        self.func = func
        self.cache_key = cache_key

    def fetch_from_api(self):
        try:
            data = self.func()
        except CantPullFromRcaApi:
            pass
        else:
            cache.set(self.cache_key, data, None)

    def get_data(self):
        data = cache.get(self.cache_key)
        if data is not None:
            return data
        return []


class AlumniStoriesAPI(_BaseContentAPI):
    def __init__(self):
        super().__init__(pull_alumni_stories, "latest_alumni_stories")


class NewsEventsAPI(_BaseContentAPI):
    def __init__(self):
        super().__init__(pull_news_and_events, "news_and_events_data")


def get_alumni_stories():
    return AlumniStoriesAPI().get_data()


def get_news_and_events():
    return NewsEventsAPI().get_data()


def fetch_student_image(image_id):
    image_fetch_result = fetch_data(
        f"{settings.API_CONTENT_BASE_URL}/api/v2/images/{image_id}/?fields=_,thumbnail",
        timeout=10,
    )
    return image_fetch_result["thumbnail"]["url"]


def parse_students_to_list(data):
    items = []
    if not data:
        return []
    for item in data.get("supervised_students", ()):
        if item.get("image"):
            item["image_url"] = fetch_student_image(item["image"])
        items.append(item)

    return items


def pull_related_students(legacy_staff_id):
    """
    Return a list of students related to legacy_staff_id
    """
    api_url = f"{settings.API_CONTENT_BASE_URL}/api/v2/pages/{legacy_staff_id}/?fields=_,supervised_students"
    # Fetch Staff
    result = fetch_data(api_url)
    # Parse to a digestable list
    result = parse_students_to_list(result)
    return result
