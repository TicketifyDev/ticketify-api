from fastapi import APIRouter, HTTPException, Query, Security, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.schemas.auth_schema import AuthModel
from src.schemas.registration_schema import organizer_registration
from src.schemas.update_profile_schema import organizer_profile_update

from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.common.constants import ORGANIZERS_COLLECTION
from src.common.db import MongoDB, MongoDBCollectionProvider
from src.common.logging_config import logger

from src.endpoints.organizer_management.organizer_register import organizer_register
from src.endpoints.organizer_management.organizer_login import organizer_login
from src.endpoints.organizer_management.organizer_status import organizer_status
from src.endpoints.organizer_management.organizer_profile import organizer_profile_get, update_organizer

router = APIRouter(prefix="/api/v1/organizers", tags=["Organizer Management"])
token = HTTPBearer()

# Create an instance of MongoDB class by providing a collection name
collection = MongoDB(ORGANIZERS_COLLECTION)

@router.post('/register',
            status_code=202,
            responses={
                202 : status_codes["response_202"],
                400 : status_codes["response_400"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def new_organizer_registration(
    details : organizer_registration, 
    collection : MongoDB = Depends(MongoDBCollectionProvider(ORGANIZERS_COLLECTION))
):
    """
    API for allowing new organizers to create accounts by providing organizer details.
    """
    logger.info("'/organizer-register' API is invoked.")
    try :
        logger.debug(f"Organizer Registration details received : {details.model_dump()}")
        response = await organizer_register(details, collection)
        logger.info("Organizer registration successful.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/organizer-register' : {exc}")
        handle_internal_server_error(exc)
    

@router.post('/login',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                500 : status_codes["response_500"]
             })
async def login_as_organizer(
    details : AuthModel, 
    request : Request, 
    collection : MongoDB = Depends(MongoDBCollectionProvider(ORGANIZERS_COLLECTION))
):
    """ 
    API for authenticating organizers and generating access tokens by validating their `username` and `password`.
    """
    logger.info("'/organizer-login' API is invoked.")
    try :
        logger.debug(f"Login attempt by organizer '{details.username}'.")
        response = await organizer_login(details, collection, request)
        logger.info("Organizer login successful.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in '/organizer-login' : {exc}")
        handle_internal_server_error(exc)


@router.get('/status',
            status_code=200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            })
async def get_organizer_status(
    username : str = Query(..., min_length=3),
    password : str = Query(...,min_length=8),
    collection : MongoDB = Depends(MongoDBCollectionProvider(ORGANIZERS_COLLECTION))
):
    """
    API for organizers to check the status of their account registration request.
    """
    logger.info("'/organizer-status' API is invoked.")
    try :
        logger.debug(f"Checking Organizer account registration request status for username '{username}'.")
        response = await organizer_status(username, password, collection)
        logger.info(f"Status retrieved for organizer '{username}'.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in '/organizer-status' : {exc}")
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
async def get_organizer_profile(
    credentials : HTTPAuthorizationCredentials = Security(token), 
    collection : MongoDB = Depends(MongoDBCollectionProvider(ORGANIZERS_COLLECTION))
):
    """
    API for retrieving logged in organizer's profile information.
    """
    logger.info("GET '/organizer-profile' API is invoked.")
    try :
        logger.debug("Validating token for organizer profile retrieval.")
        response = await organizer_profile_get(credentials, collection)
        logger.info("Organizer profile retrieved successfully.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in GET '/organizer-profile' : {exc}")
        handle_internal_server_error(exc)


@router.patch('/profile',
            status_code=200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                409 : status_codes["response_409"],
                500 : status_codes["response_500"]
            })
async def update_organizer_profile(
    details : organizer_profile_update,
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(ORGANIZERS_COLLECTION))
):
    """
    API for organizers to update their profile information.
    """
    logger.info("PATCH '/organizer-profile' API is invoked.")
    try :
        logger.debug(f"Update details received : {details.model_dump()}")
        response = await update_organizer(details, credentials, collection)
        logger.info("Organizer profile updated successfully.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in PATCH '/organizer-profile' : {exc}")
        handle_internal_server_error(exc)