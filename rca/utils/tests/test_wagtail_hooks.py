from django.test import TestCase
from django.urls import reverse
from wagtail.snippets.models import get_snippet_models
from wagtail.test.utils import WagtailTestUtils

from rca.programmes.models import DegreeLevel, ProgrammeStudyMode, ProgrammeType


class TaxonomiesViewSetGroupTest(WagtailTestUtils, TestCase):
    """Tests for the taxonomy admin migrated from wagtail-modeladmin to a
    ModelViewSetGroup in rca/utils/wagtail_hooks.py."""

    def setUp(self):
        self.user = self.login()

    def test_taxonomy_index_views_resolve_and_load(self):
        for url_namespace in [
            "degreelevel",
            "programmetype",
            "programmestudymode",
            "subject",
            "author",
            "eventtype",
            "scholarshiplocation",
        ]:
            with self.subTest(url_namespace=url_namespace):
                response = self.client.get(reverse(f"{url_namespace}:index"))
                self.assertEqual(response.status_code, 200)

    def test_taxonomy_crud(self):
        response = self.client.post(
            reverse("degreelevel:add"), {"title": "Postgraduate"}
        )
        self.assertEqual(response.status_code, 302)
        obj = DegreeLevel.objects.get(title="Postgraduate")

        response = self.client.post(
            reverse("degreelevel:edit", args=[obj.pk]), {"title": "Updated"}
        )
        self.assertEqual(response.status_code, 302)
        obj.refresh_from_db()
        self.assertEqual(obj.title, "Updated")

        response = self.client.post(reverse("degreelevel:delete", args=[obj.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DegreeLevel.objects.filter(pk=obj.pk).exists())

    def test_taxonomies_menu_group_registered(self):
        # The grouped "Taxonomies" menu is preserved with its members in order.
        from rca.utils.wagtail_hooks import TaxonomiesViewSetGroup

        group = TaxonomiesViewSetGroup()
        self.assertEqual(group.menu_label, "Taxonomies")
        self.assertEqual(group.menu_icon, "tag")
        member_models = [item.model for item in group.items]
        # First three members preserve the original submenu order.
        self.assertEqual(
            member_models[:3],
            [DegreeLevel, ProgrammeType, ProgrammeStudyMode],
        )
        self.assertEqual(len(group.items), 22)

    def test_taxonomies_menu_appears_in_admin(self):
        response = self.client.get(reverse("wagtailadmin_home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Taxonomies")

    def test_taxonomies_not_registered_as_snippets(self):
        # ModelViewSet keeps these out of the Snippets index and FK fields on
        # pages stay as select dropdowns rather than chooser modals.
        snippet_models = get_snippet_models()
        self.assertNotIn(ProgrammeType, snippet_models)
        self.assertNotIn(ProgrammeStudyMode, snippet_models)
        self.assertNotIn(DegreeLevel, snippet_models)


class ProgrammeTypeReorderTest(WagtailTestUtils, TestCase):
    def setUp(self):
        self.user = self.login()

    def test_reorder_url_is_enabled(self):
        # Native ModelViewSet reorder is wired because ProgrammeType subclasses
        # wagtail.models.Orderable (auto-detected sort_order_field).
        obj = ProgrammeType.objects.create(display_name="Type A")
        self.assertTrue(reverse("programmetype:reorder", args=[obj.pk]))

    def test_new_instance_gets_sort_order_via_admin_create(self):
        # wagtail.models.Orderable does not auto-assign sort_order in save(),
        # but the create view's set_max_order does.
        response = self.client.post(
            reverse("programmetype:add"),
            {"display_name": "First", "description": ""},
        )
        self.assertEqual(response.status_code, 302)
        first = ProgrammeType.objects.get(display_name="First")
        self.assertIsNotNone(first.sort_order)

        response = self.client.post(
            reverse("programmetype:add"),
            {"display_name": "Second", "description": ""},
        )
        self.assertEqual(response.status_code, 302)
        second = ProgrammeType.objects.get(display_name="Second")
        self.assertIsNotNone(second.sort_order)
        self.assertGreater(second.sort_order, first.sort_order)

    def test_index_ordered_by_sort_order(self):
        ProgrammeType.objects.create(display_name="ZZZ_first", sort_order=1)
        ProgrammeType.objects.create(display_name="AAA_second", sort_order=2)
        response = self.client.get(reverse("programmetype:index"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertLess(content.index("ZZZ_first"), content.index("AAA_second"))


class ProgrammeStudyModeAddSuppressionTest(WagtailTestUtils, TestCase):
    def setUp(self):
        self.user = self.login()

    def _add_url(self):
        return reverse("programmestudymode:add")

    def test_add_button_visible_below_two(self):
        # A data migration seeds two study modes; trim to one to assert the
        # add button is offered when fewer than two instances exist.
        ProgrammeStudyMode.objects.all().delete()
        ProgrammeStudyMode.objects.create(title="Full time")
        self.assertEqual(ProgrammeStudyMode.objects.count(), 1)
        response = self.client.get(reverse("programmestudymode:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{self._add_url()}"')

    def test_add_button_hidden_at_two_or_more(self):
        # The data migration already seeds two instances.
        self.assertGreaterEqual(ProgrammeStudyMode.objects.count(), 2)
        response = self.client.get(reverse("programmestudymode:index"))
        self.assertEqual(response.status_code, 200)
        # The "Add" header button should not be rendered once two exist.
        self.assertNotContains(response, f'href="{self._add_url()}"')
