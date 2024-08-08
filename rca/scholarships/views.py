from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from wagtail.admin import messages

from rca.programmes.models import ProgrammePage
from rca.utils.views import MetaTitleMixin

from .forms import ScholarshipSubmissionForm
from .models import (
    Scholarship,
    ScholarshipEnquiryFormSubmission,
    ScholarshipsListingPage,
)


def scholarships_delete(request):
    if not request.user.has_perm(
        "scholarship_enquiry_form_submission:can_delete_scholarship_enquiry_form_submission"
    ):
        raise PermissionDenied()

    from .wagtail_hooks import ScholarshipEnquiryFormSubmissionAdmin

    url_helper = ScholarshipEnquiryFormSubmissionAdmin().url_helper
    index_url = url_helper.get_action_url("index")

    all_submissions = ScholarshipEnquiryFormSubmission.objects.all()

    time_threshold = timezone.now() - timedelta(days=7)
    instances = all_submissions.filter(Q(submission_date__lte=time_threshold))
    count_delete_submissions = len(instances)

    if request.method == "POST":
        instances.delete()

        message_content = f"deleted {count_delete_submissions} submissions"
        messages.success(request, message_content)

        return redirect(index_url)

    return TemplateResponse(
        request,
        "scholarships/confirm_delete.html",
        {
            "count_all_submissions": len(all_submissions),
            "count_delete_submissions": count_delete_submissions,
            "index_url": url_helper.get_action_url("index"),
            "submit_url": (reverse("scholarships_delete")),
        },
    )


def load_scholarships(request):
    scholarships = Scholarship.objects.all()
    programme = request.GET.get("programme")

    if programme:
        try:
            # if programme is an int, search by programme page id
            programme = int(programme)
            programme_page = ProgrammePage.objects.get(id=programme)
        except (ProgrammePage.DoesNotExist, ValueError):
            # if not, search by slug
            try:
                programme_page = ProgrammePage.objects.get(slug=programme)
            except ProgrammePage.DoesNotExist:
                programme_page = None
                scholarships = scholarships.none()

        if programme_page:
            scholarships = scholarships.filter(eligable_programmes=programme_page)

    return JsonResponse(
        [{"id": s.id, "title": str(s)} for s in scholarships], safe=False
    )


class ScholarshipEnquiryFormView(MetaTitleMixin, CreateView):
    meta_title = "Express your interest in a Scholarship"
    template_name = "patterns/pages/scholarships/scholarship_form_page.html"
    form_class = ScholarshipSubmissionForm
    success_url = reverse_lazy("scholarships:scholarship_enquiry_form_thanks")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scholarships_listing_page = ScholarshipsListingPage.objects.first()
        if scholarships_listing_page:
            context["page"] = {
                "title": "Express your interest in a Scholarship",
                "introduction": scholarships_listing_page.form_introduction,
                "key_details": scholarships_listing_page.key_details,
            }
        return context

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        programme_slug = self.request.GET.get("programme")
        if programme_slug:
            try:
                programme = ProgrammePage.objects.get(slug=programme_slug)
            except Exception:
                pass
            else:
                kwargs.update({"programme": programme})
        return kwargs


class ScholarshipEnquiryFormThanksView(MetaTitleMixin, TemplateView):
    meta_title = "Thank for your interest"
    template_name = "patterns/pages/scholarships/scholarship_form_thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scholarships_listing_page = ScholarshipsListingPage.objects.first()
        if scholarships_listing_page:
            try:
                context["call_to_action"] = scholarships_listing_page.cta_block[0].value
            except Exception:
                # catch all the things so as not to crash the page.
                pass
        return context
