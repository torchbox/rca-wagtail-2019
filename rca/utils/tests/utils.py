import re
from collections import Counter

from django.db import connection
from django.test.utils import CaptureQueriesContext, override_settings

# Without REDIS_URL, as in CI, the settings fall back to Django's database
# cache, so every cache read and write shows up as a query. Image renditions
# are cached once per image on a page, which would look like growth.
LOCMEM_CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}


class QueryCountMixin:
    """Test helpers for catching queries that grow with the data."""

    def assertQueryCountDoesNotGrow(self, action, grow):
        """
        Fail if ``action`` runs more queries after ``grow`` has added data.

        ``action`` runs once before counting starts, so one-off work on a
        first request, such as creating site settings, doesn't count.

        Caching uses local memory here, so only database queries count,
        whichever cache backend the settings pick.
        """
        with override_settings(CACHES=LOCMEM_CACHES):
            self._assertQueryCountDoesNotGrow(action, grow)

    def _assertQueryCountDoesNotGrow(self, action, grow):
        action()
        with CaptureQueriesContext(connection) as before:
            action()
        # An action that runs no queries can't show growth, for example one
        # that reads a cached_property from the same object each time.
        self.assertGreater(len(before), 0, "action() ran no queries to count.")
        grow()
        with CaptureQueriesContext(connection) as after:
            action()

        # Only growth fails: a count that drops after adding data isn't
        # the problem this checks for.
        if len(after) > len(before):
            added = Counter(map(_shape, _sql(after))) - Counter(
                map(_shape, _sql(before))
            )
            details = "\n".join(f"  +{n} x {sql}" for sql, n in added.most_common())
            self.fail(
                f"Query count grew from {len(before)} to {len(after)} after "
                f"adding data. Queries added:\n{details}"
            )


def _sql(context):
    return [query["sql"] for query in context.captured_queries]


def _shape(sql):
    """``sql`` with its numbers replaced, so repeats of one query match."""
    return re.sub(r"\b\d+\b", "N", sql)[:300]
