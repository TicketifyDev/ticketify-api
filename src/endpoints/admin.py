from fastapi import APIRouter, HTTPException, status, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.common.status_codes import status_codes
from src.common.utils import response_content
from src.endpoints.admin_management.pending_organizer_requests import pending_organizer_registration_requests
import traceback

router = APIRouter(tags=["Admin Management"])
token = HTTPBearer()

@router.get('/pending-organizer-requests',
            status_code = 200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            }
        )
async def get_pending_organizer_registration_requests(credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    API for administrators to view all registration requests submitted by Organizers that are `under_review`.
    """
    try:
        response = await pending_organizer_registration_requests(credentials)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{exc}' : {exception_details}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_content(
                500,
                "An unexpected error occurred. Please try again later.",
                errors=[
                    {
                        "field": "general", 
                        "message": str(exc)
                    }
                ]
            )
        )