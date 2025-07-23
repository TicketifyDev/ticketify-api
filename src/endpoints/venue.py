from fastapi import APIRouter, HTTPException, Security, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.venue_manager_schema import VenueManagerRegistration
from src.schemas.auth_schema import AuthModel

from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.common.constants import VENUE_MANAGERS_COLLECTION
from src.common.db import MongoDB, MongoDBCollectionProvider
from src.common.logging_config import logger

from src.endpoints.venue_management.venue_manager_register import venue_manager_register
from src.endpoints.venue_management.venue_manager_login import venueManager_login

router = APIRouter(prefix="/api/v1", tags=["Venue Management"])
token = HTTPBearer()

# Create an instance of MongoDB class by providing a collection name
collection = MongoDB(VENUE_MANAGERS_COLLECTION)

@router.post('/venue-managers/register',
            status_code=201,
            responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def new_venue_manager_registration(
    details : VenueManagerRegistration, 
    collection : MongoDB = Depends(MongoDBCollectionProvider(VENUE_MANAGERS_COLLECTION))
):
    """
    API for allowing new venue managers to create accounts by providing his details.
    """
    logger.info("'/venue-mangers/register' API is invoked.")
    try :
        logger.debug(f"Venue Manager Registration details received : {details.model_dump()}")
        response = await venue_manager_register(details, collection)
        logger.info("Venue Manager registration successful.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/venue-manager/register' : {exc}")
        handle_internal_server_error(exc)


@router.post('/login',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                500 : status_codes["response_500"]
             })
async def venue_manager_login(
    details : AuthModel, 
    request : Request,
    venue_manager_collection : MongoDB = Depends(MongoDBCollectionProvider(VENUE_MANAGERS_COLLECTION))
    ):

    """ 
    API for authenticating venue manager and generating access tokens by validating their `username` and `password`.
    """
    logger.info("'/venue_managers/login' API is invoked.")
    try :
        logger.debug(f"Login attempt by venue manager '{details.username}'.")
        response = await venueManager_login(details, venue_manager_collection, request)
        logger.info("Admin login successful.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in '/venue_managers/login' : {exc}")
        handle_internal_server_error(exc)
