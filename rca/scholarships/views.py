from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse
from django.utils import timezone
from wagtail.admin import messages

from rca.scholarships.models import ScholarshipEnquiryFormSubmission


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
