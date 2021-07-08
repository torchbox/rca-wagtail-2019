from datetime import timedelta

from django.core import signing
from django.core.signing import TimestampSigner
from django.http import Http404
from django.shortcuts import get_object_or_404
from wagtail.core.models import PageRevision


def student_profile_preview(request, id_signed_string):
    revision_id = signing.loads(id_signed_string)

    # Optionally limit the age of the preview ID signing
    # Requires timestamp signing when the link is created
    # signer = TimestampSigner()
    # try:
    #     revision_id = signer.unsign(id_signed_string, max_age=timedelta(days=7))
    # except signing.SignatureExpired:
    #     raise Http404

    revision = get_object_or_404(PageRevision, id=revision_id)

    return revision.as_page_object().make_preview_request(
        original_request=request,
        # extra_request_attrs={
        #     "wagtailreview_mode": "view",
        #     "wagtailreview_reviewer": reviewer,
        # },
    )


# TODO: Add a preview link to a tab on the StudentPage edit page with help text
# link_url = reverse("student_profile_preview", kwargs={id_signed_string=signed_revision_id})

# To create signed_revision_id for link:
# from django.core import signing
# signing.dumps(p.get_latest_revision().id)

# To create signed_revision_id for link (timed):
# from django.core.signing import TimestampSigner
# signer = TimestampSigner()
# signer.sign(p.get_latest_revision().id)
# '11413:1m1WZf:MkT7MX0a_1aDetTEEf3h4bsCENK1C_vmYfwzqZuvbYQ'
