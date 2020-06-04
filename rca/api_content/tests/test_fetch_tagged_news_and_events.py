import datetime
from unittest.mock import call, patch

from django.test import TestCase

from rca.api_content.content import pull_tagged_news_and_events

FAKE_EVENT = {
    "type": "Event",
    "original_date": "2018-04-25",
    "description": "25 April 2018",
    "title": "School of Communication Film Seminar: Text and Image",
    "link": "http://example.com",
}

FAKE_NEWS = {
    "type": "News",
    "original_date": "2019-09-12",
    "description": "12 September 2019",
    "title": "RCA Innovation Workshop in Kyoto, Japan, explores design thinking for an aging society",
    "link": "http://example.com",
}


def generate_fake_events(num=3):
    for i in range(num):
        yield FAKE_EVENT


def generate_fake_news(num=3, dates=None):
    # fake news item are always published on the 1st Jan
    dates = dates or [
        datetime.date(2021, 1, 1),
        datetime.date(2020, 1, 1),
        datetime.date(2019, 1, 1),
    ]
    for i in range(num):
        item = FAKE_NEWS.copy()
        item["original_date"] = dates[i].strftime("%Y-%m-%d")
        item["description"] = dates[i].strftime("%-d  %B %Y")
        yield item


def generate_fake_blogs(num=3):
    # fake blogs are always published on the 31st Jan
    dates = [
        datetime.date(2021, 1, 31),
        datetime.date(2020, 1, 31),
        datetime.date(2019, 1, 31),
    ]
    yield from generate_fake_news(num=num, dates=dates)


@patch("rca.api_content.content.fetch_data", return_value={"items": []})
class PullTaggedNewsAndEventsTests(TestCase):
    def setUp(self):
        super().setUp()
        # pull_tagged_news_and_events() is always called with these
        self.test_tags = ("foo", "bar", "baz")
        # to query the API, pull_tagged_news_and_events() converts
        # the tag list to a comma-separated string
        self.tags_string = ",".join(self.test_tags)

    # `parse_items_to_list` is used to turn all api results into
    # nice lists, so we'll mock that to return the values we want
    @patch(
        "rca.api_content.content.parse_items_to_list",
        side_effect=[
            # when called with events, return 3 fake items
            list(generate_fake_events(3)),
            # when called with blogs, return 3 fake items
            list(generate_fake_blogs(3)),
            # when called with news, return 3 fake items
            list(generate_fake_news(3)),
        ],
    )
    def test_default(self, mocked_items_to_list, mocked_fetch_data):
        """
        By default, include 1 news/blog followed by 2 events (when available)
        """
        result = pull_tagged_news_and_events(*self.test_tags)

        # There should be 3 items total
        self.assertEqual(len(result), 3)

        # The first item should be a news/blog item
        self.assertEqual(result[0]["type"], "News")

        # AND that news/blog item should have the latest possible date
        # from generate_fake_blogs() or generate_fake_news()
        self.assertEqual(result[0]["original_date"], "2021-01-31")

        # The second and third items should be events
        self.assertEqual([result[1]["type"], result[2]["type"]], ["Event", "Event"])

        # fetch_data() should have been called 3 times to find
        # EventItems, RcaBlogPages and NewsItems
        url = "https://rca.ac.uk/api/v2/pages/"
        expected_fetch_data_calls = [
            call(
                url,
                type="rca.EventItem",
                limit=3,
                event_date_from=True,
                tags=self.tags_string,
            ),
            call(
                url,
                type="rca.RcaBlogPage",
                limit=1,
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
            call(
                url,
                type="rca.NewsItem",
                limit=1,
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
        ]
        mocked_fetch_data.assert_has_calls(expected_fetch_data_calls)

    @patch(
        "rca.api_content.content.parse_items_to_list",
        side_effect=[
            # when called with events, return only 1 item
            list(generate_fake_events(1)),
            # when called with blogs, return no items
            [],
            # when called with news, return 3 fake items
            list(generate_fake_news(3)),
        ],
    )
    def test_single_event(self, mocked_items_to_list, mocked_fetch_data):
        """
        If there is only 1 matching event, show 2 news articles (or as many as are available), followed by the event
        """
        result = pull_tagged_news_and_events(*self.test_tags)

        # There should be 3 items total
        self.assertEqual(len(result), 3)

        # The first twos items should be news/blog items
        self.assertEqual([result[0]["type"], result[1]["type"]], ["News", "News"])

        # AND the dates for those items should be the latest
        # available from generate_fake_news() - because we're
        # not including any blog results this time
        self.assertEqual(
            [result[0]["original_date"], result[1]["original_date"]],
            ["2021-01-01", "2020-01-01"],
        )

        # The third item should be an event
        self.assertEqual(result[2]["type"], "Event")

        # fetch_data() should have been called 3 times to find
        # EventItems, RcaBlogPages and NewsItems
        url = "https://rca.ac.uk/api/v2/pages/"
        expected_fetch_data_calls = [
            call(
                url,
                type="rca.EventItem",
                limit=3,
                event_date_from=True,
                tags=self.tags_string,
            ),
            call(
                url,
                type="rca.RcaBlogPage",
                limit=2,  # note: more items being fetched
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
            call(
                url,
                type="rca.NewsItem",
                limit=2,  # note: more items being fetched
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
        ]
        mocked_fetch_data.assert_has_calls(expected_fetch_data_calls)

    @patch(
        "rca.api_content.content.parse_items_to_list",
        side_effect=[
            # when called with events, return no items
            [],
            # when called with blogs, return 3 fake items
            list(generate_fake_blogs(3)),
            # when called with news, return 3 fake items
            list(generate_fake_news(3)),
        ],
    )
    def test_zero_events(self, mocked_items_to_list, mocked_fetch_data):
        """
        If there are no matching events, include 3 articles (or as many as are available).
        """
        result = pull_tagged_news_and_events(*self.test_tags)

        # There should be 3 items total
        self.assertEqual(len(result), 3)

        # All items should be news items or blogs
        self.assertEqual(
            [result[0]["type"], result[1]["type"], result[2]["type"]],
            ["News", "News", "News"],
        )

        # AND those items should have the latest possible dates
        # from generate_fake_blogs() or generate_fake_news()
        self.assertEqual(
            [
                result[0]["original_date"],
                result[1]["original_date"],
                result[2]["original_date"],
            ],
            ["2021-01-31", "2021-01-01", "2020-01-31"],
        )

        # fetch_data() should have been called 3 times to find
        # EventItems, RcaBlogPages and NewsItems
        url = "https://rca.ac.uk/api/v2/pages/"
        expected_fetch_data_calls = [
            call(
                url,
                type="rca.EventItem",
                limit=3,
                event_date_from=True,
                tags=self.tags_string,
            ),
            call(
                url,
                type="rca.RcaBlogPage",
                limit=3,  # note: more items being fetched
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
            call(
                url,
                type="rca.NewsItem",
                limit=3,  # note: more items being fetched
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
        ]
        mocked_fetch_data.assert_has_calls(expected_fetch_data_calls)

    @patch(
        "rca.api_content.content.parse_items_to_list",
        side_effect=[
            # when called with events, return 3 items
            list(generate_fake_events(3)),
            # when called with blogs, return no items
            [],
            # when called with news, return no items
            [],
        ],
    )
    def test_zero_news(self, mocked_items_to_list, mocked_fetch_data):
        """
        If there are no matching articles, show 3 events (or as many as are available).
        """
        result = pull_tagged_news_and_events(*self.test_tags)

        # There should be 3 items total
        self.assertEqual(len(result), 3)

        # All items should be events
        self.assertEqual(
            [result[0]["type"], result[1]["type"], result[2]["type"]],
            ["Event", "Event", "Event"],
        )

        # fetch_data() should have been called 3 times to find
        # EventItems, RcaBlogPages and NewsItems
        url = "https://rca.ac.uk/api/v2/pages/"
        expected_fetch_data_calls = [
            call(
                url,
                type="rca.EventItem",
                limit=3,
                event_date_from=True,
                tags=self.tags_string,
            ),
            call(
                url,
                type="rca.RcaBlogPage",
                limit=1,  # note: back to the minumum number
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
            call(
                url,
                type="rca.NewsItem",
                limit=1,  # note: back to the minumum number
                order="-date",
                tags=self.tags_string,
                tags_not="Alumni_Story",
            ),
        ]
        mocked_fetch_data.assert_has_calls(expected_fetch_data_calls)
