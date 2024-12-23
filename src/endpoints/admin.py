from fastapi import APIRouter, HTTPException, Security, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.auth_schema import AuthModel
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.endpoints.admin_management.admin_login import admin_login
from src.endpoints.admin_management.organizer_requests import organizer_registration_requests
from src.endpoints.admin_management.review_organizer_request import review_organizer_registration_request
from src.common.constants import ADMINS_COLLECTION
from src.common.constants import ORGANIZERS_COLLECTION
from src.common.db import MongoDB
from enum import Enum

router = APIRouter(prefix="/api/v1", tags=["Admin Management"])
token = HTTPBearer()

# Create an instance of MongoDB class by providing a collection name
collection = MongoDB(ADMINS_COLLECTION)
organizers_collection = MongoDB(ORGANIZERS_COLLECTION)


class RegistrationStatus(str, Enum):
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReviewRequest(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


@router.post('/admin-login',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                500 : status_codes["response_500"]
             })
async def login_as_admin(details : AuthModel, request : Request):

    """ 
    API for authenticating admins and generating access tokens by validating their `username` and `password`.
    """
    try :
        response = await admin_login(details, collection, request)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)
        

@router.get('/profile',
            status_code=200,
            responses={

            })
async def get_admin_profile():
    # Admin Profile implementation goes here
    pass


@router.post('/add',
            status_code=200,
            responses={

            })
async def add_new_admin():
    # Add new Admin implementation goes here
    pass




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

        
@router.patch('/organizers-review/{username}',
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


@router.get('/event-requests',
            status_code=200,
            responses={

            })
async def get_admin_profile():
    # implementation goes here
    pass
