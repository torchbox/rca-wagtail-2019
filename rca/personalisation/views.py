from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from wagtail.models import Page, Site
from wagtail_personalisation.wagtail_hooks import segment_user, set_visit_count


@never_cache
@require_GET
def personalisation_ctas(request, page_id):
    from rca.utils.models import BasePage

    site = Site.find_for_request(request)
    if site is None:
        return HttpResponseNotFound()

    page = (
        Page.objects.live()
        .descendant_of(site.root_page, inclusive=True)
        .filter(pk=page_id)
        .specific()
        .first()
    )
    if not isinstance(page, BasePage) or page.get_view_restrictions().exists():
        return HttpResponseNotFound()

    set_visit_count(page, request, (), {})
    segment_user(page, request, (), {})
    return TemplateResponse(
        request,
        "patterns/includes/personalisation_fragments.html",
        page.get_personalised_cta_context(request),
    )
