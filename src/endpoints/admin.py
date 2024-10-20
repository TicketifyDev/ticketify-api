from fastapi import APIRouter, HTTPException, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.endpoints.admin_management.organizer_requests import organizer_registration_requests
from src.common.db import MongoDB
from src.common.constants import ORGANIZERS_COLLECTION
from enum import Enum

router = APIRouter(prefix="/api/v1", tags=["Admin Management"])
token = HTTPBearer()

organizers_collection = MongoDB(ORGANIZERS_COLLECTION)

class RegistrationStatus(str, Enum):
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

@router.get('/organizer-requests',
            status_code = 200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            }
        )
async def get_organizer_registration_requests(
    credentials : HTTPAuthorizationCredentials = Security(token),
    status : RegistrationStatus = None,
    page : int = Query(1, description="Page number"),
    page_size : int = Query(10, description="Number of records per page")
    ):
    """
    API for administrators to view organizer registration requests based on their registration status.\n

    Args:\n
        status : The registration status to filter by
        page : The current page number (default = 1)
        page_size : The number of records per page (default = 10)
    """
    try:
        response = await organizer_registration_requests(credentials, organizers_collection, status, page, page_size)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)