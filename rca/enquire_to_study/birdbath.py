from birdbath.processors import BaseModelDeleter

from rca.enquire_to_study.models import EnquiryFormSubmission


class EnquiryFormSubmissionDeleter(BaseModelDeleter):
    """
    Delete EnquiryFormSubmission's
    """

    model = EnquiryFormSubmission
