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
    CollapsibleNavigationCTAPageType,
    CollapsibleNavigationCTASegment,
    EmbeddedFooterCTAPageType,
    EmbeddedFooterCTASegment,
    EventCountdownCTAPageType,
    EventCountdownCTASegment,
    UserActionCTAPageType,
    UserActionCTASegment,
)
from rca.standardpages.models import InformationPage


class PersonalisationCTATests(TestCase):
    """
    Tests that the correct CTAs are displayed based on segments,
    page types, and scheduling in `BasePage.get_context`.
    """

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
    def test_user_action_cta_appears_when_conditions_met(self, mock_get_adapter):
        """Test that UserActionCallToAction appears when all conditions are met"""
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

    @patch("rca.utils.models.get_segment_adapter")
    def test_user_action_cta_not_shown_when_segment_not_active(self, mock_get_adapter):
        """Test that CTA doesn't appear when user's segment doesn't match"""
        # Setup - user has student segment, but CTA is for alumni
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_students]
        )

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=now - timedelta(days=1),
        )

        UserActionCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertNotIn("personalised_user_cta", response.context)

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_when_no_segments_active(self, mock_get_adapter):
        """Test that CTAs don't appear when user has no active segments"""
        # Setup - no segments active
        mock_get_adapter.return_value = self._create_mock_segment_adapter([])

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=timezone.now(),
        )

        UserActionCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertNotIn("personalised_user_cta", response.context)

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_for_wrong_page_type(self, mock_get_adapter):
        """Test that CTA doesn't appear on wrong page type"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=now - timedelta(days=1),
        )

        UserActionCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        # CTA is configured for programme pages, not information pages
        UserActionCTAPageType.objects.create(
            call_to_action=cta, page_type="programmes.programmepage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertNotIn("personalised_user_cta", response.context)

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_before_go_live_date(self, mock_get_adapter):
        """Test that CTA doesn't appear before go_live_at date"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=now + timedelta(days=1),  # Go live tomorrow
        )

        UserActionCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertNotIn("personalised_user_cta", response.context)

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_after_expire_date(self, mock_get_adapter):
        """Test that CTA doesn't appear after expire_at date"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=now - timedelta(days=7),
            expire_at=now - timedelta(days=1),  # Expired yesterday
        )

        UserActionCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertNotIn("personalised_user_cta", response.context)

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_not_shown_when_both_dates_blank(self, mock_get_adapter):
        """Test that CTA is disabled when both go_live_at and expire_at are blank"""
        # Setup
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=None,
            expire_at=None,
        )

        UserActionCTASegment.objects.create(
            call_to_action=cta, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert
        self.assertNotIn("personalised_user_cta", response.context)

    @patch("rca.utils.models.get_segment_adapter")
    def test_embedded_footer_cta_appears_when_conditions_met(self, mock_get_adapter):
        """Test that EmbeddedFooterCallToAction appears in context"""
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

    @patch("rca.utils.models.get_segment_adapter")
    def test_event_countdown_cta_appears_when_conditions_met(self, mock_get_adapter):
        """Test that EventCountdownCallToAction appears in context"""
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

    @patch("rca.utils.models.get_segment_adapter")
    def test_collapsible_nav_cta_appears_when_conditions_met(self, mock_get_adapter):
        """Test that CollapsibleNavigationCallToAction appears in context"""
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

    @patch("rca.utils.models.get_segment_adapter")
    def test_only_first_matching_cta_is_shown(self, mock_get_adapter):
        """
        Test that when multiple CTAs of the same type match,
        only the first one is shown
        """
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        # Create two matching CTAs
        cta1 = UserActionCallToActionFactory(
            title="First CTA",
            external_link="https://example.com/first",
            go_live_at=now - timedelta(days=2),
        )
        UserActionCTASegment.objects.create(
            call_to_action=cta1, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta1, page_type="standardpages.informationpage"
        )

        cta2 = UserActionCallToActionFactory(
            title="Second CTA",
            external_link="https://example.com/second",
            go_live_at=now - timedelta(days=1),
        )
        UserActionCTASegment.objects.create(
            call_to_action=cta2, segment=self.segment_alumni
        )
        UserActionCTAPageType.objects.create(
            call_to_action=cta2, page_type="standardpages.informationpage"
        )

        # Execute
        response = self.client.get(self.test_page.url)

        # Assert - only one should appear (first one returned by query)
        self.assertIn("personalised_user_cta", response.context)
        # The title should be from one of the CTAs
        self.assertIn(
            response.context["personalised_user_cta"]["title"],
            ["First CTA", "Second CTA"],
        )

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_with_only_go_live_at_set(self, mock_get_adapter):
        """Test that CTA works with only go_live_at set (no expire_at)"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=now - timedelta(days=1),
            expire_at=None,
        )

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

    @patch("rca.utils.models.get_segment_adapter")
    def test_cta_with_only_expire_at_set(self, mock_get_adapter):
        """Test that CTA works with only expire_at set (no go_live_at)"""
        # Setup
        now = timezone.now()
        mock_get_adapter.return_value = self._create_mock_segment_adapter(
            [self.segment_alumni]
        )

        cta = UserActionCallToActionFactory(
            external_link="https://example.com",
            go_live_at=None,
            expire_at=now + timedelta(days=7),
        )

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
