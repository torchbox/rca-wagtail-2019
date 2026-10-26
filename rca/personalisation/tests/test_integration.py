from datetime import timedelta

import wagtail_factories
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Site
from wagtail.test.utils.form_data import inline_formset, nested_form_data
from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import OriginCountryRule

from rca.home.models import HomePage
from rca.personalisation.factories import (
    CollapsibleNavigationCallToActionFactory,
    EmbeddedFooterCallToActionFactory,
    EventCountdownCallToActionFactory,
    SegmentFactory,
    UserActionCallToActionFactory,
)
from rca.personalisation.models import (
    CollapsibleNavigationCTAPage,
    CollapsibleNavigationCTASegment,
    EmbeddedFooterCTAPage,
    EmbeddedFooterCTASegment,
    EventCountdownCTAPage,
    EventCountdownCTASegment,
    OriginContinentRule,
    UserActionCTAPage,
    UserActionCTASegment,
    UserTypeRule,
)
from rca.standardpages.models import InformationPage
from rca.users.factories import UserFactory


class InformationPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = InformationPage

    title = "Personalisation integration"
    introduction = "Personalisation integration test page"


class PersonalisationIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page = InformationPageFactory(parent=HomePage.objects.first())

    def create_cta(self, factory, segment_model, page_model, segment, **kwargs):
        cta = factory(go_live_at=timezone.now() - timedelta(days=1), **kwargs)
        segment_model.objects.create(call_to_action=cta, segment=segment)
        page_model.objects.create(call_to_action=cta, page=self.page)
        return cta

    def test_segment_visit_count_increases_once_per_request(self):
        segment = SegmentFactory(type="dynamic")
        OriginCountryRule.objects.create(segment=segment, country="gb")
        self.create_cta(
            UserActionCallToActionFactory,
            UserActionCTASegment,
            UserActionCTAPage,
            segment,
            external_link="https://example.com/audience",
        )

        for expected_count in [1, 2]:
            response = self.client.get(self.page.url, headers={"cf-ipcountry": "GB"})
            self.assertEqual(response.status_code, 200)
            self.assertIn("personalised_user_cta", response.context)
            segment.refresh_from_db()
            self.assertEqual(segment.visit_count, expected_count)

    def test_preview_and_direct_rendering_evaluate_segments_once(self):
        segment = SegmentFactory(type="dynamic")
        OriginCountryRule.objects.create(segment=segment, country="gb")
        self.create_cta(
            UserActionCallToActionFactory,
            UserActionCTASegment,
            UserActionCTAPage,
            segment,
            title="Preview audience popup",
            external_link="https://example.com/preview",
        )

        for expected_count, preview in enumerate([True, False], start=1):
            with self.subTest(preview=preview):
                request = RequestFactory().get(
                    self.page.url, headers={"cf-ipcountry": "GB"}
                )
                request.session = self.client.session
                request.user = AnonymousUser()
                request.site = Site.find_for_request(request)
                if preview:
                    response = self.page.serve_preview(request, "")
                else:
                    response = self.page.serve(request)
                response.render()

                self.assertContains(response, "Preview audience popup")
                self.assertIn("personalised_user_cta", response.context_data)
                self.assertIn("personalised_user_cta", self.page.get_context(request))
                segment.refresh_from_db()
                self.assertEqual(segment.visit_count, expected_count)

    def test_editor_override_only_shows_the_selected_segment(self):
        matching_segment = SegmentFactory(type="dynamic")
        OriginCountryRule.objects.create(segment=matching_segment, country="gb")
        forced_segment = SegmentFactory(type="dynamic")
        OriginCountryRule.objects.create(segment=forced_segment, country="us")
        self.create_cta(
            UserActionCallToActionFactory,
            UserActionCTASegment,
            UserActionCTAPage,
            matching_segment,
            external_link="https://example.com/matching",
        )
        self.create_cta(
            EmbeddedFooterCallToActionFactory,
            EmbeddedFooterCTASegment,
            EmbeddedFooterCTAPage,
            forced_segment,
            external_link="https://example.com/forced",
        )
        self.client.force_login(UserFactory(is_superuser=True, is_staff=True))

        response = self.client.get(
            self.page.url,
            {"segment": forced_segment.pk},
            headers={"cf-ipcountry": "GB"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("personalised_footer_cta", response.context)
        self.assertNotIn("personalised_user_cta", response.context)

    def test_anonymous_visitors_cannot_force_a_segment(self):
        segment = SegmentFactory(type="dynamic")
        OriginCountryRule.objects.create(segment=segment, country="us")
        self.create_cta(
            UserActionCallToActionFactory,
            UserActionCTASegment,
            UserActionCTAPage,
            segment,
            external_link="https://example.com/restricted-audience",
        )

        response = self.client.get(
            self.page.url,
            {"segment": segment.pk},
            headers={"cf-ipcountry": "GB"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("personalised_user_cta", response.context)

    def test_new_and_returning_visitors_receive_different_ctas(self):
        new_segment = SegmentFactory(type="dynamic", persistent=False)
        returning_segment = SegmentFactory(type="dynamic", persistent=False)
        UserTypeRule.objects.create(segment=new_segment, user_type="new")
        UserTypeRule.objects.create(segment=returning_segment, user_type="returning")
        self.create_cta(
            UserActionCallToActionFactory,
            UserActionCTASegment,
            UserActionCTAPage,
            new_segment,
            external_link="https://example.com/new",
        )
        self.create_cta(
            EmbeddedFooterCallToActionFactory,
            EmbeddedFooterCTASegment,
            EmbeddedFooterCTAPage,
            returning_segment,
            external_link="https://example.com/returning",
        )

        first_response = self.client.get(self.page.url)
        self.assertEqual(first_response.status_code, 200)
        self.assertIn("personalised_user_cta", first_response.context)
        self.assertNotIn("personalised_footer_cta", first_response.context)
        self.assertIn("no-store", first_response["Cache-Control"])

        second_response = self.client.get(self.page.url)
        self.assertEqual(second_response.status_code, 200)
        self.assertNotIn("personalised_user_cta", second_response.context)
        self.assertIn("personalised_footer_cta", second_response.context)
        self.assertIn("no-store", second_response["Cache-Control"])
        self.assertEqual(
            sum(visit["count"] for visit in self.client.session["visit_count"]), 2
        )

        fresh_response = Client().get(self.page.url)
        self.assertIn("personalised_user_cta", fresh_response.context)
        self.assertNotIn("personalised_footer_cta", fresh_response.context)

    def test_country_and_continent_rules_target_countdown_and_navigation(self):
        segment = SegmentFactory(type="dynamic", persistent=False, match_any=False)
        OriginCountryRule.objects.create(segment=segment, country="gb")
        OriginContinentRule.objects.create(segment=segment, continent="EU")
        self.create_cta(
            EventCountdownCallToActionFactory,
            EventCountdownCTASegment,
            EventCountdownCTAPage,
            segment,
            external_link="https://example.com/event",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            countdown_to="start",
        )
        self.create_cta(
            CollapsibleNavigationCallToActionFactory,
            CollapsibleNavigationCTASegment,
            CollapsibleNavigationCTAPage,
            segment,
        )

        for headers, matches in [
            ({"HTTP_CF_IPCOUNTRY": "GB", "HTTP_CF_IPCONTINENT": "EU"}, True),
            ({"HTTP_CF_IPCOUNTRY": "GB"}, True),
            ({"HTTP_CF_IPCOUNTRY": "FR"}, False),
            ({"HTTP_CF_IPCOUNTRY": "GB", "HTTP_CF_IPCONTINENT": "NA"}, False),
            ({}, False),
        ]:
            with self.subTest(headers=headers):
                response = Client().get(self.page.url, **headers)
                self.assertEqual(response.status_code, 200)
                for key in (
                    "personalised_countdown_cta",
                    "personalised_collapsible_nav",
                ):
                    self.assertEqual(key in response.context, matches)
                self.assertEqual(
                    "no-store" in response.get("Cache-Control", ""), matches
                )

    def test_persistent_segment_survives_a_change_in_country(self):
        segment = SegmentFactory(type="dynamic", persistent=True)
        OriginCountryRule.objects.create(segment=segment, country="gb")
        self.create_cta(
            UserActionCallToActionFactory,
            UserActionCTASegment,
            UserActionCTAPage,
            segment,
            external_link="https://example.com/persistent",
        )

        for country in ["GB", "US"]:
            with self.subTest(country=country):
                response = self.client.get(
                    self.page.url, headers={"cf-ipcountry": country}
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("personalised_user_cta", response.context)

    def test_segment_admin_can_create_and_edit_custom_rules(self):
        SegmentFactory(type="dynamic", name="Existing audience")
        self.client.force_login(UserFactory(is_superuser=True, is_staff=True))
        create_url = reverse("wagtail_personalisation_segment_modeladmin_create")
        response = self.client.get(create_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "personalisation_usertyperules")
        self.assertContains(response, "personalisation_origincontinentrules")

        data = {
            "name": "Custom rule integration",
            "status": "enabled",
            "type": "dynamic",
            "count": "0",
            "randomisation_percent": "",
        }
        for relation_name in response.context["form"].formsets:
            data[relation_name] = inline_formset([])
        data["personalisation_usertyperules"] = inline_formset(
            [{"user_type": "returning"}]
        )
        data["personalisation_origincontinentrules"] = inline_formset(
            [{"continent": "EU"}]
        )

        response = self.client.post(create_url, nested_form_data(data))
        self.assertEqual(response.status_code, 302)
        segment = Segment.objects.get(name="Custom rule integration")
        user_rule = UserTypeRule.objects.get(segment=segment)
        continent_rule = OriginContinentRule.objects.get(segment=segment)
        self.assertEqual(user_rule.user_type, "returning")
        self.assertEqual(continent_rule.continent, "EU")

        edit_url = reverse(
            "wagtail_personalisation_segment_modeladmin_edit", args=[segment.pk]
        )
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)

        data["personalisation_usertyperules"] = inline_formset(
            [{"id": user_rule.pk, "user_type": "new"}], initial=1
        )
        data["personalisation_origincontinentrules"] = inline_formset(
            [{"id": continent_rule.pk, "continent": "NA"}], initial=1
        )
        response = self.client.post(edit_url, nested_form_data(data))
        self.assertEqual(response.status_code, 302)
        user_rule.refresh_from_db()
        continent_rule.refresh_from_db()
        self.assertEqual(user_rule.user_type, "new")
        self.assertEqual(continent_rule.continent, "NA")
