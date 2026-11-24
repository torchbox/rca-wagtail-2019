from django.apps import apps as django_apps
from django.test import RequestFactory, TestCase
from wagtail import hooks
from wagtail.admin.userbar import apply_userbar_hooks
from wagtail_personalisation import wagtail_hooks as wp_hooks

from rca.personalisation.factories import SegmentFactory
from rca.personalisation.wagtail_hooks import remove_personalisation_segments


class PatchPersonalisationUserbarHookTests(TestCase):
    """
    Covers rca.personalisation.apps.PersonalisationConfig
    ._patch_personalisation_userbar_hook, which wraps
    wagtail_personalisation's two-argument construct_wagtail_userbar hook so
    Wagtail 8.1's three-argument call doesn't raise TypeError.
    """

    def setUp(self):
        self.app_config = django_apps.get_app_config("personalisation")

    def test_patch_adds_segment_item_without_type_error(self):
        # PersonalisationConfig.ready() already applied the patch when
        # Django started for this test run. Isolate the patched hook and
        # confirm it both accepts the 3-argument call Wagtail 8.1 makes and
        # still performs wagtail-personalisation's real behaviour: adding a
        # userbar item for each enabled segment.
        SegmentFactory()
        request = RequestFactory().get("/")
        patched_hook = next(
            fn
            for fn in hooks.get_hooks("construct_wagtail_userbar")
            if "_patch_personalisation_userbar_hook" in fn.__qualname__
        )
        items = []

        # Wagtail 8.1 calls every construct_wagtail_userbar hook as
        # (request, items, page). Without the patch this raises:
        #   TypeError: add_segment_link_items() takes 2 positional
        #   arguments but 3 were given
        patched_hook(request, items, page=None)

        self.assertEqual(len(items), 1)

    def test_segments_still_filtered_from_userbar_end_to_end(self):
        # The full Wagtail 8.1 call path: wagtail-personalisation's (patched)
        # hook adds a link item for the enabled segment, and rca's own
        # remove_personalisation_segments (also called with the 3-argument
        # signature) strips it back out, same as before the Wagtail 8.1
        # upgrade.
        SegmentFactory()
        request = RequestFactory().get("/")
        items = []

        apply_userbar_hooks(request, items, page=None)

        self.assertEqual(items, [])

    def test_remove_personalisation_segments_filters_segment_items(self):
        # Unit-level check that the project's own hook still does its job
        # under Wagtail 8.1's 3-argument call, independent of whatever
        # wagtail-personalisation's hook adds.
        request = RequestFactory().get("/")
        kept_item = object()
        segment_item = type("Item", (), {"segment": object()})()
        items = [kept_item, segment_item]

        remove_personalisation_segments(request, items, page=None)

        self.assertEqual(items, [kept_item])

    def test_missing_attribute_is_logged_instead_of_crashing_on_startup(self):
        original_fn = wp_hooks.add_segment_link_items
        del wp_hooks.add_segment_link_items
        try:
            with self.assertLogs("rca.personalisation.apps", level="WARNING") as cm:
                self.app_config._patch_personalisation_userbar_hook()
        finally:
            wp_hooks.add_segment_link_items = original_fn

        self.assertIn("add_segment_link_items", cm.output[0])

    def test_hook_not_found_is_logged_instead_of_silently_no_opping(self):
        # Calling the patch method again can no longer find the hook by
        # identity in wagtail's registry - the first call already replaced
        # it with a wrapping closure. Confirm that's logged rather than
        # silently discarded.
        self.assertTrue(
            any(
                fn is not wp_hooks.add_segment_link_items
                for fn, _order in hooks._hooks.get("construct_wagtail_userbar", [])
            )
        )

        with self.assertLogs("rca.personalisation.apps", level="WARNING") as cm:
            self.app_config._patch_personalisation_userbar_hook()

        self.assertIn("not found", cm.output[0].lower())
