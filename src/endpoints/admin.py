from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
# from src.endpoints.admin_management.pending_organizer_requests import pending_organizer_registration_requests
from src.endpoints.admin_management.review_organizer_request import review_organizer_registration_request
from src.common.db import MongoDB
from src.common.constants import ORGANIZERS_COLLECTION
from src.schemas.review_request_schema import ReviewRequest


router = APIRouter(tags=["Admin Management"])
token = HTTPBearer()

organizers_collection = MongoDB(ORGANIZERS_COLLECTION)

# @router.get('/pending-organizer-requests',
#             status_code = 200,
#             responses={
#                 400 : status_codes["response_400"],
#                 401 : status_codes["response_401"],
#                 403 : status_codes["response_401"],
#                 404 : status_codes["response_404"],
#                 500 : status_codes["response_500"]
#             }
#         )
# async def get_pending_organizer_registration_requests(credentials : HTTPAuthorizationCredentials = Security(token)):
#     """
#     API for administrators to view all registration requests submitted by Organizers that are `under_review`.
#     """
#     try:
#         response = await pending_organizer_registration_requests(credentials, organizers_collection)
#         return response

#     except HTTPException as http_exc:
#         raise http_exc

#     except Exception as exc :
#         handle_internal_server_error(exc)

@router.patch('/review-organizer-request/{username}',
              status_code = 200,
              responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            })
async def review_organizer_registration(
    username : str,
    review : ReviewRequest,
    credentials : HTTPAuthorizationCredentials = Security(token)
):
    """
    API for administrators to review and approve/reject an organizer's registration request.
    """
    try :
        response = await review_organizer_registration_request(
            username,
            review,
            organizers_collection,
            credentials
        )
        return response
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e :
        handle_internal_server_error(e)

    