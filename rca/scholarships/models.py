from urllib.parse import urlencode

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.models import register_snippet

from rca.programmes.models import ProgrammePage
from rca.scholarships.filters import ScholarshipsTabStyleFilter
from rca.utils.models import BasePage


@register_snippet
class ScholarshipSnippet(ClusterableModel):
    title = models.CharField(max_length=255,)
    programme = models.ManyToManyField(ProgrammePage)

    def __str__(self):
        return self.title

    panels = [FieldPanel("title"), FieldPanel("programme")]


class ScholarshipListingPage(BasePage):
    template = "patterns/pages/editorial/editorial_listing.html"

    def get_active_filters(self, request):
        return {
            "programme": request.GET.getlist("programme"),
        }

    def get_extra_query_params(self, request, active_filters):
        extra_query_params = []
        for filter_name in active_filters:
            for filter_id in active_filters[filter_name]:
                extra_query_params.append(urlencode({filter_name: filter_id}))
        return extra_query_params

    def get_base_queryset(self):
        return ScholarshipSnippet.objects.all()

    def modify_results(self, paginator_page, request):
        for obj in paginator_page.object_list:
            # TODO other field data
            obj.title = obj.title

    def get_context(self, request, *args, **kwargs):
        from rca.programmes.models import ProgrammePage

        context = super().get_context(request, *args, **kwargs)

        base_queryset = self.get_base_queryset()
        queryset = base_queryset.all()

        filters = (
            ScholarshipsTabStyleFilter(
                "Programme",
                queryset=(
                    ProgrammePage.objects.filter(
                        id__in=base_queryset.values_list("programme__id", flat=True,)
                    ).live()
                ),
                filter_by="programme__slug__in",
                option_value_field="slug",
            ),
        )
        # Apply filters
        for f in filters:
            queryset = f.apply(queryset, request.GET)

        # Paginate filtered queryset
        per_page = 12

        page_number = request.GET.get("page")
        paginator = Paginator(queryset, per_page)
        try:
            results = paginator.page(page_number)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        # Set additional attributes etc
        self.modify_results(results, request)

        # Finalise and return context
        context.update(
            filters={
                "title": "Filter by",
                "aria_label": "Filter results",
                "items": filters,
            },
            results=results,
            result_count=paginator.count,
        )

        return context
