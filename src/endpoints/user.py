from fastapi import APIRouter, HTTPException, Security, Request, Depends
from src.schemas.auth_schema import AuthModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.common.constants import USERS_COLLECTION
from src.schemas.registration_schema import user_registration
from src.schemas.update_profile_schema import update_user_details
from src.common.db import MongoDB, MongoDBCollectionProvider
from src.common.status_codes import status_codes
from src.common.logging_config import logger

from src.common.utils import handle_internal_server_error
from src.endpoints.user_management.user_register import user_register
from src.endpoints.user_management.user_login import user_login
from src.endpoints.user_management.get_user_profile import get_user_profile
from src.endpoints.user_management.update_user import update_user

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])
token = HTTPBearer()

@router.post('/register',
            status_code=201,
            responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def new_user_registration(
    details : user_registration,
    collection : MongoDB = Depends(MongoDBCollectionProvider(USERS_COLLECTION))
):
    """
    API for allowing new users to create accounts by providing user details.
    """
    logger.info("POST '/users/register' API is invoked.")
    try:
        logger.debug(f"User Registration details received : {details.model_dump()}")
        response = await user_register(details, collection)
        logger.info("User registration successful.")
        return response
    
    except HTTPException as e :
        raise e

    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/users/register' : {exc}")
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
async def login_user(
    details : AuthModel, 
    request :Request,
    collection : MongoDB = Depends(MongoDBCollectionProvider(USERS_COLLECTION))
):
    """
    API where users can login to there accounts by providing valid username and password
    """
    logger.info(" POST'/users/login' API is invoked.")
    try:
        logger.debug(f"Login attempt by user '{details.username}'.")
        response = await user_login(details, collection, request)
        logger.info("User logged in successfully.")
        return response
    
    except HTTPException as e :
        raise e

    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/users/login' for user: {exc}")
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
async def fetch_user_profile(
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(USERS_COLLECTION))
):
    """
    API for retrieving logged-in user's profile information.
    """
    logger.info("GET '/user/profile' API is invoked.")
    try :
        logger.debug("Validating token for user profile retrieval.")
        response = await get_user_profile(credentials, collection)
        logger.info("User profile retrieved successfully.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in GET '/user/profile' : {exc}")
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
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(USERS_COLLECTION))
):
    """
    API for Users to update their profile information.
    """
    logger.info("PATCH '/user/update' API is invoked.")
    try :
        logger.debug(f"Update details received for user with details : {details.model_dump()}")
        response = await update_user(details, credentials, collection)
        logger.info("User profile updated successfully.")
        return response

    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in PATCH '/user/update' : {exc}")
        handle_internal_server_error(exc)


