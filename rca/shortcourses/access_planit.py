import logging

import requests
from bs4 import BeautifulSoup as bs
from django.conf import settings
from django.core.cache import cache
from django.http.request import QueryDict
from django.utils.dateparse import parse_datetime
from requests.exceptions import Timeout

"""
Provides functionality for fetching data from access planit xml feed
"""


logger = logging.getLogger(__name__)


class AccessPlanitException(Exception):
    pass


class AccessPlanitXMLParser:
    """ XML parses
    xml: a blob of xml to a list (from response.text)
    """

    def __init__(self, xml):
        self.xml = xml

    def get_parsed_data(self):
        """ Parses the given xml to a list
            return: list or None
        """
        bs_content = bs(self.xml, "lxml")
        course_dates = bs_content.find("dates").find_all("wicoursedate")
        items = None
        if course_dates:
            items = []
            for i in course_dates:
                item = {
                    "course_date_id": i.coursedateid.text,
                    "course_id": i.courseid.text,
                    "cost": i.cost.text,
                    "start_date": parse_datetime(i.startdate.text),
                    "end_date": parse_datetime(i.enddate.text),
                    "spaces_available": i.spacesavailable.text,
                    "status": i.status.text,
                    "book_now_url": i.booknowurl.text,
                    "enquire_url": i.enquireurl.text,
                }
                items.append(item)

        return items


class AccessPlanitXML:
    """Used for retrieving short course data from the AccessPlanit xml feeds.
    The data is periodically fetched with a management command and set
    in the low-level cache.

    Raises:
        AccessPlanitException: Should the fetch encouter Timeouts or any other
        exceptions, this raised and caught when setting the data in the cache.
    """

    def __init__(self, course_id=0):
        self.course_id = course_id
        self.company_id = settings.ACCESS_PLANIT_SCHOOL_ID
        self.cache_key = f"short_course_{self.course_id}"
        self.timeout = 10

    def prepare_query(self):
        """ Returns a URL to query """
        self.query = QueryDict(mutable=True)
        self.query.update(
            {
                "CompanyID": self.company_id,
                "courseIDs": self.course_id,
                "venueIDs": "",
                "categoryIDs": "",
            }
        )
        self.query = self.query.urlencode()
        if settings.ACCESS_PLANIT_XML_BASE_URL:
            return settings.ACCESS_PLANIT_XML_BASE_URL + self.query

    def parse_data(self, xml_data):
        parser = AccessPlanitXMLParser(xml=xml_data)
        return parser.get_parsed_data()

    def fetch_data_from_xml(self):
        url = self.prepare_query()
        try:
            response = requests.get(url=url)
        except Timeout:
            if settings.API_FETCH_LOGGING:
                logger.exception(
                    f"Timeout occurred fetching XML data for course_id: {self.course_id}"
                )
            raise AccessPlanitException
        except Exception:
            if settings.API_FETCH_LOGGING:
                logger.exception(
                    f"Error occurred fetching XML data for course_id: {self.course_id}"
                )
            raise AccessPlanitException
        else:
            return self.parse_data(response.text)

    def get_and_set_data_in_cache(self):
        """ Method to try getting data from the XML feed
        and setting it in the cache.
        """
        try:
            data = self.fetch_data_from_xml()
        except AccessPlanitException:
            # If trying to fetch data raises AccessPlanitException, pass it
            # return what's currently in the cache
            pass
        else:
            cache.set(self.cache_key, data, settings.ACCESS_PLANIT_XML_FEED_TIMEOUT)

        return cache.get(self.cache_key)

    def get_data(self):
        """ Fetch the data from the cache, if there is None, re-populate it.
        Cache is periodically populated by the management command via cron"""
        short_course_data = cache.get(self.cache_key)
        if short_course_data is None:
            short_course_data = self.get_and_set_data_in_cache()
        return short_course_data


class AccessPlanitCourseChecker:
    """Used for checking a course exists using the AccessPlanit xml feeds.

    Raises:
        AccessPlanitException: Should the fetch encounter Timeouts or any other
        exceptions, this raised and caught when setting the data in the cache.
    """

    def __init__(self, course_id=0):
        self.course_id = course_id
        self.company_id = settings.ACCESS_PLANIT_SCHOOL_ID
        self.timeout = 10

    def prepare_query(self):
        """ Returns a URL to query """
        self.query = QueryDict(mutable=True)
        self.query.update(
            {
                "CompanyID": self.company_id,
                "courseIDs": self.course_id,
                "venueIDs": "",
                "categoryIDs": "",
            }
        )
        self.query = self.query.urlencode()
        if settings.ACCESS_PLANIT_XML_COURSE_URL:
            return settings.ACCESS_PLANIT_XML_COURSE_URL + self.query

    def fetch_course_data(self):
        url = self.prepare_query()
        try:
            response = requests.get(url=url)
        except Timeout:
            if settings.API_FETCH_LOGGING:
                logger.exception(
                    f"Timeout occurred fetching XML data for course_id: {self.course_id}"
                )
            raise AccessPlanitException
        except Exception:
            if settings.API_FETCH_LOGGING:
                logger.exception(
                    f"Error occurred fetching XML data for course_id: {self.course_id}"
                )
            raise AccessPlanitException
        else:
            return response.text

    def course_exists(self):
        course_data = self.fetch_course_data()
        if course_data:
            bs_content = bs(course_data, "lxml")
            courses = bs_content.find_all("wicourse")
            return len(courses) > 0
