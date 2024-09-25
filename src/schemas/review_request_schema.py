from enum import Enum

class ReviewRequest(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"