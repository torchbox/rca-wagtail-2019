import logging

from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from rca.scholarships.models import ScholarshipSnippet

from .forms import ScholarshipForm

logger = logging.getLogger(__name__)


def load_scholarships(request):
    programme = request.GET.get("programme")
    if programme:
        scholarships = ScholarshipSnippet.objects.filter(
            programme__id=programme
        ).order_by("title")

        return render(
            request,
            "patterns/pages/scholarships/includes/scholarships_choices.html",
            {"scholarships": scholarships},
        )


class ScholarshipFormView(FormView):

    form_class = ScholarshipForm
    success_url = "/"
    template_name = "patterns/pages/scholarships/scholarship_enquiry.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)
