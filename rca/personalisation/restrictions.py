from contextlib import contextmanager
from contextvars import ContextVar

_view_restrictions = ContextVar("personalisation_view_restrictions", default=None)


@contextmanager
def cache_page_view_restrictions(request):
    """Reuse restriction querysets for one read-only request, then discard them."""
    token = _view_restrictions.set({} if request.method in ("GET", "HEAD") else None)
    try:
        yield
    finally:
        _view_restrictions.reset(token)


def get_cached_view_restrictions(page, load_restrictions):
    querysets = _view_restrictions.get()
    if querysets is None or page.pk is None:
        return load_restrictions()

    key = (page._state.db, page.pk)
    if key not in querysets:
        querysets[key] = load_restrictions()
    return querysets[key]
