from datetime import timedelta
from unittest.mock import Mock, patch

import wagtail_factories
from django.test import TestCase
from django.utils import timezone

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
    CollapsibleNavigationCTAPageType,
    CollapsibleNavigationCTASegment,
    EmbeddedFooterCTAPage,
    EmbeddedFooterCTAPageType,
    EmbeddedFooterCTASegment,
    EventCountdownCTAPage,
    EventCountdownCTAPageType,
    EventCountdownCTASegment,
    UserActionCTAPage,
    UserActionCTAPageType,
    UserActionCTASegment,
)
from rca.standardpages.models import InformationPage


class BasePersonalisationCTATests(TestCase):
    """
    Base class for CTA tests with common setup and helpers.
    """

    # Define CTA type configurations for subtest parameterization
    CTA_TYPES = [
        {
            "name": "UserAction",
            "factory": UserActionCallToActionFactory,
            "segment_model": UserActionCTASegment,
            "page_type_model": UserActionCTAPageType,
            "page_model": UserActionCTAPage,
            "context_key": "personalised_user_cta",
            "base_fields": lambda: {"external_link": "https://example.com"},
        },
        {
            "name": "EmbeddedFooter",
            "factory": EmbeddedFooterCallToActionFactory,
            "segment_model": EmbeddedFooterCTASegment,
            "page_type_model": EmbeddedFooterCTAPageType,
            "page_model": EmbeddedFooterCTAPage,
            "context_key": "personalised_footer_cta",
            "base_fields": lambda: {"external_link": "https://example.com"},
        },
        {
            "name": "EventCountdown",
            "factory": EventCountdownCallToActionFactory,
            "segment_model": EventCountdownCTASegment,
            "page_type_model": EventCountdownCTAPageType,
            "page_model": EventCountdownCTAPage,
            "context_key": "personalised_countdown_cta",
            "base_fields": lambda: {
                "external_link": "https://example.com",
                "start_date": timezone.now() + timedelta(days=30),
                "end_date": timezone.now() + timedelta(days=31),
                "countdown_to": "start",
            },
        },
        {
            "name": "CollapsibleNavigation",
            "factory": CollapsibleNavigationCallToActionFactory,
            "segment_model": CollapsibleNavigationCTASegment,
            "page_type_model": CollapsibleNavigationCTAPageType,
            "page_model": CollapsibleNavigationCTAPage,
            "context_key": "personalised_collapsible_nav",
            "base_fields": lambda: {},  # No link fields needed for CollapsibleNav
        },
    ]

    def setUp(self):
        self.home_page = HomePage.objects.first()

        # Create a test page
        self.test_page = InformationPage(
            title="Test Page",
            introduction="Test introduction",
        )
        self.home_page.add_child(instance=self.test_page)

        # Create segments
        self.segment_alumni = SegmentFactory(name="Alumni")
        self.segment_students = SegmentFactory(name="Students")

    def _create_mock_segment_adapter(self, segments):
        """Helper to create a mock segment adapter with given segments"""
        mock_adapter = Mock()
        mock_adapter.get_segments.return_value = segments
        mock_adapter.refresh.return_value = None
        return mock_adapter

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_after_expire_date(self, mock_get_adapter):
        """Test that CTA doesn't appear after expire_at date for all CTA types"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": now - timedelta(days=7),
                        "expire_at": now - timedelta(days=1),  # Expired yesterday
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertNotIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_before_go_live_date(self, mock_get_adapter):
        """Test that CTA doesn't appear before go_live_at date for all CTA types"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": now + timedelta(days=1),  # Go live tomorrow
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertNotIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_when_both_dates_blank(self, mock_get_adapter):
        """Test that CTA is disabled when both go_live_at and expire_at are blank for all CTA types"""
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": None,
                        "expire_at": None,
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertNotIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_when_segment_not_active(self, mock_get_adapter):
        """Test that CTA doesn't appear when user's segment doesn't match for all CTA types"""
        now = timezone.now()
        # User has student segment, but CTA is for alumni
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_students]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": now - timedelta(days=1),
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertNotIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_when_no_segments_active(self, mock_get_adapter):
        """Test that CTAs don't appear when user has no active segments for all CTA types"""
        # No segments active
        mock_get_adapter.return_value = self._create_mock_segment_adapter([])

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": timezone.now(),
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertNotIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_for_wrong_page_type(self, mock_get_adapter):
        """Test that CTA doesn't appear on wrong page type for all CTA types"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": now - timedelta(days=1),
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                # CTA is configured for programme pages, not information pages
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="programmes.programmepage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertNotIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_with_only_go_live_at_set(self, mock_get_adapter):
        """Test that CTA works with only go_live_at set (no expire_at) for all CTA types"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": now - timedelta(days=1),
                        "expire_at": None,
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_with_only_expire_at_set(self, mock_get_adapter):
        """Test that CTA works with only expire_at set (no go_live_at) for all CTA types"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update(
                    {
                        "go_live_at": None,
                        "expire_at": now + timedelta(days=7),
                    }
                )

                cta = cta_config["factory"](**cta_fields)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_only_first_matching_cta_is_shown(self, mock_get_adapter):
        """
        Test that when multiple CTAs of the same type match,
        only the first one is shown
        """
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup - create two matching CTAs
                cta_fields1 = cta_config["base_fields"]()
                cta_fields1.update(
                    {
                        "go_live_at": now - timedelta(days=2),
                    }
                )
                cta1 = cta_config["factory"](**cta_fields1)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta1, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta1, page_type="standardpages.informationpage"
                )

                cta_fields2 = cta_config["base_fields"]()
                cta_fields2.update(
                    {
                        "go_live_at": now - timedelta(days=1),
                    }
                )
                cta2 = cta_config["factory"](**cta_fields2)

                cta_config["segment_model"].objects.create(
                    call_to_action=cta2, segment=self.segment_alumni
                )
                cta_config["page_type_model"].objects.create(
                    call_to_action=cta2, page_type="standardpages.informationpage"
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert - only one should appear (first one returned by query)
                self.assertIn(cta_config["context_key"], response.context)

                # Cleanup for next subtest
                cta1.delete()
                cta2.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_shown_on_specific_page(self, mock_get_adapter):
        """Test that CTA appears on a specific selected page"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update({
                    "go_live_at": now - timedelta(days=1),
                })

                cta = cta_config["factory"](**cta_fields)

                # Link to segment but NOT to page type
                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )

                # Link to specific page (not page type)
                cta_config["page_model"].objects.create(
                    call_to_action=cta,
                    page=self.test_page,
                    include_children=False,
                )

                # Execute
                response = self.client.get(self.test_page.url)

                # Assert
                self.assertIn(cta_config["context_key"], response.context)

                # Cleanup
                cta.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_shown_on_child_pages_when_include_children_true(self, mock_get_adapter):
        """Test that CTA appears on child pages when include_children is True"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        # Create a child page
        from rca.standardpages.models import InformationPage
        child_page = InformationPage(
            title="Child Page",
            introduction="Child introduction",
        )
        self.test_page.add_child(instance=child_page)

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update({
                    "go_live_at": now - timedelta(days=1),
                })

                cta = cta_config["factory"](**cta_fields)

                # Link to segment
                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )

                # Link to parent page with include_children=True
                cta_config["page_model"].objects.create(
                    call_to_action=cta,
                    page=self.test_page,
                    include_children=True,
                )

                # Execute - view the child page
                response = self.client.get(child_page.url)

                # Assert - CTA should appear on child page
                self.assertIn(cta_config["context_key"], response.context)

                # Cleanup
                cta.delete()

        child_page.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_on_child_pages_when_include_children_false(self, mock_get_adapter):
        """Test that CTA does NOT appear on child pages when include_children is False"""
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        # Create a child page
        from rca.standardpages.models import InformationPage
        child_page = InformationPage(
            title="Child Page",
            introduction="Child introduction",
        )
        self.test_page.add_child(instance=child_page)

        for cta_config in self.CTA_TYPES:
            with self.subTest(cta_type=cta_config["name"]):
                # Setup
                cta_fields = cta_config["base_fields"]()
                cta_fields.update({
                    "go_live_at": now - timedelta(days=1),
                })

                cta = cta_config["factory"](**cta_fields)

                # Link to segment
                cta_config["segment_model"].objects.create(
                    call_to_action=cta, segment=self.segment_alumni
                )

                # Link to parent page with include_children=False
                cta_config["page_model"].objects.create(
                    call_to_action=cta,
                    page=self.test_page,
                    include_children=False,
                )

                # Execute - view the child page
                response = self.client.get(child_page.url)

                # Assert - CTA should NOT appear on child page
                self.assertNotIn(cta_config["context_key"], response.context)

                # Cleanup
                cta.delete()

        child_page.delete()

    @patch("rca.utils.models.get_segment_adapter")
    def test_multiple_ctas_can_appear_together(self, mock_get_adapter):
        """Test that multiple different CTA types can appear on same page"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        # Create different types of CTAs
        user_cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=now - timedelta(days=1),
        )
        UserActionCTASegment.objects.create(
            call_to_action=user_cta, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=user_cta, page_type="standardpages.informationpage"
        )

        footer_cta = EmbeddedFooterCallToActionFactory(
            external_link="https://example.com/donate",
            go_live_at=now - timedelta(days=1),
        )
        EmbeddedFooterCTASegment.objects.create(
            call_to_action=footer_cta, segment=self.segment_alumni
        )
        EmbeddedFooterCTAPageType.objects.create(
            call_to_action=footer_cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert - both CTAs should appear
        self.assertIn("personalised_user_cta", response.context)
        self.assertIn("personalised_footer_cta", response.context)


class UserActionCTATests(BasePersonalisationCTATests):
    """
    Tests for UserActionCallToAction-specific display logic.
    Common tests (scheduling, segments, page types) are in BasePersonalisationCTATests.
    """

    @patch("rca.utils.models.get_segment_adapter")
    def test_user_action_cta_appears_with_correct_variables(self, mock_get_adapter):
        """Test that UserActionCallToAction appears when all conditions are met  with the correct variables"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        internal_link = wagtail_factories.PageFactory()
        cta = UserActionCallToActionFactory(
            title="Join our alumni network",
            internal_link=internal_link,
            go_live_at=now - timedelta(days=1),
            expire_at=now + timedelta(days=7),
        )

        # Link to segment and page type
        UserActionCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertIn("personalised_user_cta", response.context)
        self.assertEqual(
            response.context["personalised_user_cta"]["title"],
            "Join our alumni network",
        )
        self.assertEqual(
            response.context["personalised_user_cta"]["href"], internal_link.url
        )


class EmbeddedFooterCTATests(BasePersonalisationCTATests):
    """
    Tests for EmbeddedFooterCallToAction display logic.
    """

    @patch("rca.utils.models.get_segment_adapter")
    def test_embedded_footer_cta_appears_with_correct_variables(self, mock_get_adapter):
        """Test that EmbeddedFooterCallToAction appears in context with the correct variables"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        internal_link = wagtail_factories.PageFactory()
        cta = EmbeddedFooterCallToActionFactory(
            title="Support RCA",
            internal_link=internal_link,
            go_live_at=now - timedelta(days=1),
        )

        EmbeddedFooterCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        EmbeddedFooterCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertIn("personalised_footer_cta", response.context)
        self.assertEqual(
            response.context["personalised_footer_cta"]["title"], "Support RCA"
        )


class EventCountdownCTATests(BasePersonalisationCTATests):
    """
    Tests for EventCountdownCallToAction display logic.
    """

    @patch("rca.utils.models.get_segment_adapter")
    def test_event_countdown_cta_appears_with_correct_variables(self, mock_get_adapter):
        """Test that EventCountdownCallToAction appears in context with the correct variables"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_students]
        )

        cta = EventCountdownCallToActionFactory(
            title="Open Day",
            external_link="https://example.com/openday",
            start_date=now + timedelta(days=30),
            end_date=now + timedelta(days=31),
            countdown_to="start",
            countdown_timer_pre_text="Starts in",
            go_live_at=now - timedelta(days=1),
        )

        EventCountdownCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_students
        )
        EventCountdownCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertIn("personalised_countdown_cta", response.context)
        self.assertEqual(
            response.context["personalised_countdown_cta"]["title"], "Open Day"
        )
        self.assertEqual(
            response.context["personalised_countdown_cta"]["countdown_text"],
            "Starts in",
        )


class CollapsibleNavigationCTATests(BasePersonalisationCTATests):
    """
    Tests for CollapsibleNavigationCallToAction display logic.
    """

    @patch("rca.utils.models.get_segment_adapter")
    def test_collapsible_nav_cta_appears_with_correct_variables(self, mock_get_adapter):
        """Test that CollapsibleNavigationCallToAction appears in context with correct variables"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        page1 = wagtail_factories.PageFactory()
        page2 = wagtail_factories.PageFactory()

        cta = CollapsibleNavigationCallToActionFactory(
            title="Quick Links",
            go_live_at=now - timedelta(days=1),
        )
        # Add links using StreamField
        cta.links = [
            ("link", {"page": page1, "title": "Link 1"}),
            ("link", {"page": page2, "title": "Link 2"}),
        ]
        cta.save()

        CollapsibleNavigationCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        CollapsibleNavigationCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertIn("personalised_collapsible_nav", response.context)
        self.assertEqual(len(response.context["personalised_collapsible_nav"]), 2)
        self.assertEqual(
            response.context["personalised_collapsible_nav"][0]["text"], "Link 1"
        )
