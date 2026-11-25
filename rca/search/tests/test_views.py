from django.db.models.signals import post_init
from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Page

from rca.home.models import HomePage
from rca.programmes.factories import ProgrammePageFactory


@override_settings(DEFAULT_PER_PAGE=5)
class SearchViewTests(TestCase):
    def setUp(self):
        self.add_matching_pages(12)

    def add_matching_pages(self, count):
        home_page = HomePage.objects.first()
        for _ in range(count):
            ProgrammePageFactory(parent=home_page, title="Zebra studies")

    def search(self, **params):
        return self.client.get(reverse("search"), params)

    def test_results_are_paginated(self):
        first = self.search(q="zebra")
        last = self.search(q="zebra", page=3)

        self.assertEqual(first.context["search_results"].paginator.count, 12)
        self.assertEqual(len(first.context["search_results"]), 5)
        self.assertEqual(len(last.context["search_results"]), 2)

    def test_page_past_the_end_shows_the_last_page(self):
        response = self.search(q="zebra", page=999)

        self.assertEqual(response.context["search_results"].number, 3)
        self.assertEqual(len(response.context["search_results"]), 2)

    def test_misspelt_query_falls_back_to_title_matches(self):
        response = self.search(q="zebar")

        titles = {page.title for page in response.context["search_results"]}
        self.assertEqual(titles, {"Zebra studies"})

    def test_query_with_no_matches_shows_no_results(self):
        response = self.search(q="xqzv")

        self.assertEqual(response.context["search_results"].paginator.count, 0)
        self.assertContains(response, "search-list__no-results")

    def test_only_one_page_of_results_is_loaded(self):
        loaded = []

        def record(sender, instance, **kwargs):
            if instance.title.startswith("Zebra"):
                loaded.append(instance)

        post_init.connect(record, sender=Page)
        try:
            self.search(q="zebra")
        finally:
            post_init.disconnect(record, sender=Page)

        self.assertEqual(len(loaded), 5)
