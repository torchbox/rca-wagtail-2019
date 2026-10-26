from datetime import timedelta

import wagtail_factories
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase
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
                response = self.client.get(self.fragment_url(page))
                self.assertEqual(response.status_code, 404)
                self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
                self.assertIn("no-store", response["Cache-Control"])

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
