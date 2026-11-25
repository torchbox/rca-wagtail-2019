# Back-end testing

This page covers running the Python tests and two patterns for catching code that does more database work than it needs to. For JavaScript tests, see [Front end tooling](front-end-tooling.md#tests).

## Running the tests

Run the tests inside the `web` container, with the test settings:

```bash
docker compose exec web python manage.py test --settings=rca.settings.test
```

To run one app or one test class, add its dotted path:

```bash
docker compose exec web python manage.py test --settings=rca.settings.test rca.search
docker compose exec web python manage.py test --settings=rca.settings.test rca.projects.tests.test_models.ProjectPickerPageTests
```

CI runs the same suite on every push (`.github/workflows/test.yaml`).

## Why these patterns matter

Code that queries the database for each item it shows often looks fine in development, where a listing has five items. In production the same listing has hundreds, and each page view runs hundreds of queries or loads hundreds of full pages.

We found several of these while working on web server memory use ([R1-405](https://torchbox.atlassian.net/browse/R1-405)). For example:

- A programme page's scholarships list loaded every eligible programme as a full page, StreamFields included, just to print their names. Each name also ran two or three queries, because `ProgrammePage.__str__` looks up the degree levels.
- Site search loaded every matching page on each request (about 2,100 for "design"), because `if not search_results:` fetched all of them before the paginator kept one page.
- The projects listing ran about 290 queries per page, because each project card looked up its school, research centre, start-up label and image on its own.

None of these broke anything, so no existing test failed. The two patterns below are for writing tests that would have failed.

## Catching queries that grow with the data

Use `QueryCountMixin` from `rca/utils/tests/utils.py` when the number of queries shouldn't depend on how much data there is. Mix it into the test case and call `assertQueryCountDoesNotGrow()`:

```python
from django.test import TestCase

from rca.utils.tests.utils import QueryCountMixin


class ProjectPickerPageTests(QueryCountMixin, TestCase):
    def test_query_count_does_not_grow_with_projects(self):
        def add_projects():
            self.add_project(school=self.school, centre=self.centre)
            self.add_project(centre=self.centre)
            self.add_project(research_type=self.startup)

        add_projects()
        self.assertQueryCountDoesNotGrow(
            action=lambda: self.client.get(self.picker.url),
            grow=add_projects,
        )
```

It runs `action` and counts its queries, runs `grow` to add data, then runs `action` again and fails if it made more queries the second time. It runs `action` once before it starts counting, because the first request in a test does one-off work, such as creating site settings rows. Counting that first request would make the counts look different when nothing had grown.

When the count grows, the failure lists the queries that were added, so you can see which lookup repeats:

```text
Query count grew from 6 to 16 after adding data. Queries added:
  +5 x SELECT "programmes_programmepagedegreelevel"... WHERE ... "source_page_id" = N ...
  +5 x SELECT "programmes_degreelevel"... WHERE "programmes_degreelevel"."id" = N LIMIT N
```

### When to add one

Add one of these tests when your change touches code that shows a list of things from the database:

- listing and index pages, including their filters and dropdowns;
- sections that loop over related items, such as related programmes, related staff or slideshows;
- API endpoints that return lists;
- a model's `__str__`, or a property or method, that's used inside a loop or a template `{% for %}`. This is how the programme page scholarships problem started: a later change made `ProgrammePage.__str__` run queries, and code that called `str()` on many pages got slower without anyone touching it.

If you fix one of these problems with `select_related()` or `prefetch_related()`, add the test with the fix, so a later change can't undo it without the test failing.

### Choosing `action` and `grow`

- `action` should do exactly what a visitor's request does: request the page, or call the method the template calls. If the method is a `cached_property`, fetch a fresh object inside `action` each time, or the second run will read the cached value and make no queries.
- `grow` has to add data that `action` actually shows. Templates often skip work for some items, so make sure the new items go down every path. For example, the project card template only looks up a project's school when the project isn't a start-up. A test that only added start-up projects passed against the slow code. The test above adds one project of each kind for this reason.
- Check that the test fails against the old code before you fix it. If it doesn't, `grow` probably isn't exercising the slow path.

## Catching code that loads too much in one query

A query count can't catch code that runs one query but fetches far too many rows. The search bug above ran the same number of queries whether 10 pages matched or 2,000. Each query just returned more rows.

The usual cause is testing a queryset as a true or false value. Both of these run the whole query and load every row:

```python
if search_results:          # loads every matching page
    ...
```

```django
{% if item.queryset %}      {# loads every row, to decide whether to show a tab #}
```

Use `exists()` to check whether there are any rows, or `count()` if you need the number. Both run a cheap query that fetches no rows.

If you only need the count to paginate, leave it to the `Paginator`, which runs its own `count()`. Calling `count()` on a Django QuerySet and then paginating it runs the `COUNT` query twice. The search view can call `count()` first because Wagtail's search results keep their count, so the paginator reuses it.

To test for this, count the model instances a request creates. The `post_init` signal fires once for each instance Django builds from a database row:

```python
from django.db.models.signals import post_init


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
```

Give the test's own data a distinctive name, such as "Zebra studies" here, and only count those instances. Other parts of the page, such as the navigation, build page objects of their own, and counting those would make the test depend on unrelated templates.

## Examples in the code

- `rca/utils/tests/utils.py`: `QueryCountMixin` itself.
- `rca/programmes/tests/test_models.py`, `ProgrammePageScholarshipItemsTests`: query count on a `cached_property`, with a fresh page in each run.
- `rca/programmes/tests/test_filter.py`, `ProgrammeStyleFilterTests`: query count on a filter's options.
- `rca/projects/tests/test_models.py`, `ProjectPickerPageTests`: query count on a listing page, with `grow` covering every path through the card template.
- `rca/search/tests/test_views.py`, `SearchViewTests`: a count of loaded pages, for a bug that a query count can't catch.
- `rca/utils/tests/test_filter.py`, `ListingFilterTabTests`: a listing that shows its Programme filter tab without loading any programme pages.
