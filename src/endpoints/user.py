from fastapi import APIRouter, HTTPException, Security, Request
from src.schemas.auth_schema import AuthModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.common.constants import USERS_COLLECTION
from src.schemas.registration_schema import user_registration
from src.schemas.update_profile_schema import update_user_details
from src.common.db import MongoDB
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.endpoints.user_management.user_register import user_register
from src.endpoints.user_management.user_login import user_login
from src.endpoints.user_management.get_user_profile import get_user_profile
from src.endpoints.user_management.update_user import update_user

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])
token = HTTPBearer()
collection = MongoDB(USERS_COLLECTION)

@router.post('/register',
            status_code=201,
            responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def new_user_registration(details : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    try:
        response = await user_register(details, collection)
        return response
    
    except HTTPException as e :
        raise e

    except Exception as exc:
        handle_internal_server_error(exc)


@router.post('/login',
            status_code=201,
            responses={
                200 : status_codes["response_200"],
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def login_user(details : AuthModel, request :Request):
    """
    API where users can login to there accounts by providing valid username and password
    """
    try:
        response = await user_login(details, collection, request)
        return response
    
    except HTTPException as e :
        raise e

    except Exception as exc:
        handle_internal_server_error(exc)


@router.get('/profile',
           status_code=200,
           responses={
               400 : status_codes["response_400"],
               401 : status_codes["response_401"],
               403 : status_codes["response_401"],
               404 : status_codes["response_404"],
               500 : status_codes["response_500"]
           })
async def fetch_user_profile(credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    API for retrieving logged-in user's profile information.
    """
    try :
        response = await get_user_profile(credentials, collection)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)


@router.patch('/update',
            status_code=200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                409 : status_codes["response_409"],
                500 : status_codes["response_500"]
            })
async def update_user_profile(
    details : update_user_details,
    credentials : HTTPAuthorizationCredentials = Security(token)
    ):
    """
    API for organizers to update their profile information.
    """
    try :
        response = await update_user(details, credentials, collection)
        return response

    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)


