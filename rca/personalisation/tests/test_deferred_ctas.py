from datetime import timedelta
from unittest.mock import patch

import wagtail_factories
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.template import engines
from django.test import Client, RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Page, PageViewRestriction, Site
from wagtail.views import serve
from wagtail_personalisation.rules import OriginCountryRule

from rca.forms.models import FormPage
from rca.home.models import HomePage
from rca.personalisation.factories import SegmentFactory, UserActionCallToActionFactory
from rca.personalisation.models import UserActionCTAPage, UserActionCTASegment
from rca.personalisation.tests.test_integration import InformationPageFactory
from rca.standardpages.models import InformationPage
from rca.users.factories import UserFactory


class FormPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = FormPage

    title = "Contact form"


class DeferredCTATests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page = InformationPageFactory(parent=HomePage.objects.first())
        cls.segment = SegmentFactory(type="dynamic")
        OriginCountryRule.objects.create(segment=cls.segment, country="gb")
        cls.cta = UserActionCallToActionFactory(
            title="Audience-specific popup",
            external_link="https://example.com/audience",
            go_live_at=timezone.now() - timedelta(days=1),
        )
        UserActionCTASegment.objects.create(call_to_action=cls.cta, segment=cls.segment)
        UserActionCTAPage.objects.create(call_to_action=cls.cta, page=cls.page)

    def fragment_url(self, page=None):
        return reverse("personalisation_ctas", args=[(page or self.page).pk])

    def test_anonymous_page_is_shared_html_without_a_session_cookie(self):
        response = self.client.get(self.page.url, headers={"cf-ipcountry": "GB"})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.cta.title)
        self.assertContains(response, 'data-personalisation-url="')
        self.assertContains(response, self.fragment_url())
        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertIn("public", response["Cache-Control"])
        self.assertNotIn("private", response["Cache-Control"])
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.visit_count, 0)

    def test_page_does_not_modify_an_existing_anonymous_session(self):
        session = self.client.session
        session["visit_count"] = [
            {"id": self.page.pk, "path": self.page.url_path, "count": 3}
        ]
        session.save()

        response = self.client.get(self.page.url, headers={"cf-ipcountry": "GB"})

        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertEqual(self.client.session["visit_count"][0]["count"], 3)
        self.assertNotContains(response, self.cta.title)

    def test_anonymous_page_queries_view_restrictions_once(self):
        # Navigation performs a separate lookup of all restricted pages.
        template = engines["django"].from_string("{{ page.title }}")
        with patch.object(
            InformationPage, "get_template", return_value=template
        ), CaptureQueriesContext(connection) as queries:
            response = self.client.get(self.page.url)

        restriction_table = PageViewRestriction._meta.db_table
        restriction_queries = [
            query["sql"]
            for query in queries.captured_queries
            if query["sql"].lstrip().upper().startswith("SELECT ")
            and f'"{restriction_table}"' in query["sql"]
        ]
        self.assertEqual(len(restriction_queries), 1, restriction_queries)
        self.assertEqual(response.status_code, 200)
        self.assertIn("public", response["Cache-Control"])

    def test_direct_and_inherited_restrictions_keep_unlocked_pages_private(self):
        child = InformationPageFactory(parent=self.page, title="Restricted child")
        UserActionCTAPage.objects.create(call_to_action=self.cta, page=child)
        restriction = PageViewRestriction.objects.create(
            page=self.page, restriction_type="password", password="test-password"
        )

        for page in [self.page, child]:
            with self.subTest(page=page.title):
                client = Client()
                blocked = client.get(page.url, headers={"cf-ipcountry": "GB"})
                self.assertContains(blocked, "csrfmiddlewaretoken")
                self.assertContains(blocked, 'name="password"')
                self.assertIn("private", blocked["Cache-Control"])

                client.post(
                    reverse(
                        "wagtailcore_authenticate_with_password",
                        args=[restriction.pk, page.pk],
                    ),
                    {"password": "test-password", "return_url": page.url},
                )
                unlocked = client.get(page.url, headers={"cf-ipcountry": "GB"})

                self.assertContains(unlocked, self.cta.title)
                self.assertNotContains(unlocked, 'data-personalisation-url="')
                self.assertIn("private", unlocked["Cache-Control"])
                self.assertIn("no-store", unlocked["Cache-Control"])
                self.assertNotIn("public", unlocked["Cache-Control"])

    def test_reused_page_instance_observes_restrictions_added_between_requests(self):
        with patch.object(Page, "route_for_request", return_value=(self.page, (), {})):
            public = self.client.get(self.page.url)
            self.assertIn("public", public["Cache-Control"])

            PageViewRestriction.objects.create(
                page=self.page, restriction_type="password", password="test-password"
            )
            blocked = self.client.get(self.page.url)

        self.assertContains(blocked, "csrfmiddlewaretoken")
        self.assertNotContains(blocked, 'data-personalisation-url="')
        self.assertIn("private", blocked["Cache-Control"])
        self.assertNotIn("public", blocked["Cache-Control"])

    def test_anonymous_preview_keeps_inline_ctas_and_private_headers(self):
        request = RequestFactory().get(self.page.url, headers={"cf-ipcountry": "GB"})
        request.user = AnonymousUser()
        request.session = self.client.session
        request.site = Site.find_for_request(request)
        request.is_preview = True

        response = serve(request, self.page.url.lstrip("/"))
        response.render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cta.title)
        self.assertNotContains(response, 'data-personalisation-url="')
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn("public", response["Cache-Control"])
        self.assertEqual(request.session["visit_count"][0]["count"], 1)
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.visit_count, 1)

    def test_shared_page_html_is_identical_for_different_visitors(self):
        first = self.client.get(self.page.url, headers={"cf-ipcountry": "GB"})
        self.client.get(self.fragment_url(), headers={"cf-ipcountry": "GB"})
        returning = self.client.get(self.page.url, headers={"cf-ipcountry": "GB"})
        other = Client().get(self.page.url, headers={"cf-ipcountry": "US"})

        self.assertEqual(first.content, returning.content)
        self.assertEqual(first.content, other.content)
        self.assertNotIn(settings.SESSION_COOKIE_NAME, returning.cookies)

    def test_fragment_targets_the_visitor_and_records_one_page_view(self):
        self.client.get(self.page.url)
        response = self.client.get(self.fragment_url(), headers={"cf-ipcountry": "GB"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cta.title)
        self.assertContains(response, 'data-personalisation-fragment="user"')
        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn("public", response["Cache-Control"])
        visits = self.client.session["visit_count"]
        self.assertEqual(
            [(visit["id"], visit["count"]) for visit in visits], [(self.page.pk, 1)]
        )
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.visit_count, 1)

    def test_non_matching_fragment_is_still_uncacheable_and_tracks_visits(self):
        response = self.client.get(self.fragment_url(), headers={"cf-ipcountry": "US"})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.cta.title)
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.session["visit_count"][0]["count"], 1)

    def test_signed_in_pages_keep_inline_ctas_and_are_private(self):
        self.client.force_login(UserFactory(is_staff=True, is_superuser=True))

        response = self.client.get(self.page.url, headers={"cf-ipcountry": "GB"})

        self.assertContains(response, self.cta.title)
        self.assertNotContains(response, 'data-personalisation-url="')
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])

    def test_signed_in_page_without_a_matching_cta_is_still_private(self):
        self.client.force_login(UserFactory(is_staff=True, is_superuser=True))

        response = self.client.get(self.page.url, headers={"cf-ipcountry": "US"})

        self.assertNotContains(response, self.cta.title)
        self.assertIn("private", response["Cache-Control"])
        self.assertNotIn("public", response["Cache-Control"])

    def test_form_pages_keep_inline_ctas_and_private_headers(self):
        page = FormPageFactory(parent=HomePage.objects.first())
        UserActionCTAPage.objects.create(call_to_action=self.cta, page=page)

        response = self.client.get(page.url, headers={"cf-ipcountry": "GB"})

        self.assertContains(response, self.cta.title)
        self.assertNotContains(response, 'data-personalisation-url="')
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])

    def test_fragment_rejects_unpublished_and_password_protected_pages(self):
        unpublished = InformationPageFactory(
            parent=HomePage.objects.first(), title="Unpublished page", live=False
        )
        restricted = InformationPageFactory(
            parent=HomePage.objects.first(), title="Restricted page"
        )
        PageViewRestriction.objects.create(
            page=restricted, restriction_type="password", password="test-only-password"
        )
        restricted_child = InformationPageFactory(parent=restricted)

        for page in [unpublished, restricted, restricted_child]:
            with self.subTest(page=page.pk):
                response = self.client.get(
                    self.fragment_url(page), headers={"cf-ipcountry": "GB"}
                )
                self.assertEqual(response.status_code, 404)
                self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
                self.assertIn("no-store", response["Cache-Control"])
                self.segment.refresh_from_db()
                self.assertEqual(self.segment.visit_count, 0)

    def test_fragment_cannot_access_pages_belonging_to_another_site(self):
        other_root = wagtail_factories.PageFactory(parent=Page.get_first_root_node())
        wagtail_factories.SiteFactory(root_page=other_root, hostname="other.example")
        page = InformationPageFactory(parent=other_root)

        response = self.client.get(self.fragment_url(page))

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)

    def test_fragment_rejects_post_without_tracking_a_visit(self):
        response = self.client.post(self.fragment_url())

        self.assertEqual(response.status_code, 405)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.visit_count, 0)
