from fastapi import APIRouter, HTTPException, Security
from src.schemas.auth_schema import AuthModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.registration_schema import user_registration
from src.common.db import MongoDB
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.endpoints.user_management.user_register import user_register
from src.endpoints.user_management.user_login import user_login
from src.endpoints.user_management.get_user_profile import get_user_profile

router = APIRouter(tags=["User Management"])
token = HTTPBearer()
collection = MongoDB("users")

@router.post('/user-register',
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

@router.post('/user-login',
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
async def login_user(details : AuthModel):
    """
    API where users can login to there accounts by providing valid username and password
    """
    try:
        response = await user_login(details, collection)
        return response
    
    except HTTPException as e :
        raise e

    except Exception as exc:
        handle_internal_server_error(exc)



@router.get('/user-profile',
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