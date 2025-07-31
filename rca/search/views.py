from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.utils.cache import add_never_cache_headers, patch_cache_control
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page

from rca.utils.cache import get_default_cache_control_kwargs

# Similarity threshold for trigram search (0.0 to 1.0)
SIMILARITY_THRESHOLD = 0.1


def search(request):
    search_query = request.GET.get("q", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        search_results = Page.objects.live().search(search_query, operator="and")
        query = Query.get(search_query)

        # Record hit
        query.add_hit()

        # If no results found, try trigram similarity search
        # We can only filter by title, since that's the only field we have
        # common to all page types.
        if not search_results:
            search_results = (
                Page.objects.live()
                .annotate(
                    similarity=TrigramSimilarity("title", search_query),
                )
                .filter(similarity__gt=SIMILARITY_THRESHOLD)
                .order_by("-similarity")
            )
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, settings.DEFAULT_PER_PAGE)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    response = TemplateResponse(
        request,
        "patterns/pages/search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
            "SEO_NOINDEX": True,
        },
    )
    # Instruct FE cache to not cache when the search query is present.
    # It's so hits get added to the database and results include newly
    # added pages.
    if search_query:
        add_never_cache_headers(response)
    else:
        patch_cache_control(response, **get_default_cache_control_kwargs())
    return response
