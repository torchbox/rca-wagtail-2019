from birdbath.processors import BaseModelDeleter

from rca.scholarships.models import ScholarshipEnquiryFormSubmission


class ScholarshipEnquiryFormSubmissionDeleter(BaseModelDeleter):
    """
    Delete ScholarshipEnquiryFormSubmission's
    """

    model = ScholarshipEnquiryFormSubmission
