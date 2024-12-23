from enum import Enum

class RegistrationStatus(str, Enum):
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReviewRequest(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"