from fastapi import APIRouter, HTTPException, Security, Request, Depends, Query
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.venue_manager_schema import VenueManagerRegistration, SeatBookedByVenueManager
from src.schemas.auth_schema import AuthModel
from src.schemas.venues_schema import VenueBase, VenueUpdateRequest
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.common.constants import VENUE_MANAGERS_COLLECTION, VENUES_COLLECTION, SHOW_SLOTS_COLLECTION
from src.common.db import MongoDB, MongoDBCollectionProvider
from src.common.logging_config import logger
from src.endpoints.venue_management.venue_manager_register import venue_manager_register
from src.endpoints.venue_management.venue_manager_login import venueManager_login
from src.endpoints.venue_management.venue_creation import create_venue
from src.endpoints.venue_management.venue_browse import get_venue
from src.endpoints.venue_management.venues_managed_by_venue_manager import venues_managed_by_logged_in_venue_manager, update_seats_bookedby_venuemanager
from src.endpoints.venue_management.venue_updation import venue_updation
from src.endpoints.venue_management.venue_deletion import venue_deletion

router = APIRouter(prefix="/api/v1", tags=["Venue Management"])
token = HTTPBearer()

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


@router.post('/venue-managers/login',
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


@router.post('/venues',
            status_code=201,
            responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def add_new_venue(
    details : VenueBase,
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(VENUES_COLLECTION))
):
    """
    API for venue managers to add a new venue(centre).
    """
    logger.info("POST '/venues' API is invoked.")
    try:
        logger.debug(f"Venue details received : {details.model_dump()}")
        response = await create_venue(credentials, details, collection)
        logger.info(f"Venue '{details.name}' added successfully.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as exc:
        logger.error(f"Unexpected error occurred in 'POST '/venues' : {exc}")
        handle_internal_server_error(exc)


@router.get('/venues',
            status_code=200,
            responses={
                200 : status_codes["response_200"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def browse_venues(
    city: str = Query(..., description="city of the venue"), 
    venue_name: Optional[str] = Query(None, description="name of the venue"), 
    collection : MongoDB = Depends(MongoDBCollectionProvider(VENUES_COLLECTION)),
    page : int = Query(1, description="Page number"),
    page_size : int = Query(10, description="Number of records per page")
):
    """
    API for users to fetch all venues(centres) and it's details available inside the specified city.
    """
    logger.info("GET '/venues' API is invoked.")
    try:
        response = await get_venue(collection, city, venue_name, page, page_size)
        logger.info("Venue(s) fetched successfully.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as exc:
        logger.error(f"Unexpected error occurred in 'GET '/venues' : {exc}")
        handle_internal_server_error(exc)



@router.patch('/venues/{venue_id}',
            status_code=200,
            responses={
                200 : status_codes["response_200"],
                204 : status_codes["response_204"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def update_venue(
    venue_id: str,
    details : VenueUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(VENUES_COLLECTION))
):
    """
    API for venue managers to update a venue added by them.
    """
    logger.info(f" PATCH '/venues/{venue_id}' API is invoked.")
    try:
        logger.debug(f"Starting the process of venue updation for venue '{venue_id}'.")
        response = await venue_updation(credentials, venue_id, details, collection)
        logger.info(f"Venue '{venue_id}' updated successfully")
        return response
    
    except HTTPException as http_exc :
        raise http_exc
    
    except Exception as exc:
        logger.error(f"Unexpected error occurred in PATCH '/venues/{venue_id}' : {exc}")
        handle_internal_server_error(exc)


@router.delete('/venues',
            status_code=200,
            responses={
                200 : status_codes["response_200"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def delete_venue(
    venue_id: str = Query(..., description="venue id for deletion"),
    credentials: HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(VENUES_COLLECTION))
):
    """
    API for venue managers to delete a venue added by them.
    For venue_id , refer Browse Venues
    """
    logger.info(" DELETE '/venues/' API is invoked.")
    try:
        logger.debug(f"Deleting the Venue with ID :'{venue_id}'.")
        response = await venue_deletion(credentials, venue_id, collection)
        logger.info(f"Venue '{venue_id}' deleted successfully")
        return response
    
    except HTTPException as http_exc :
        raise http_exc
    
    except Exception as exc:
        logger.error(f"Unexpected error occurred in DELETE '/venues/{venue_id}' : {exc}")
        handle_internal_server_error(exc)


@router.get('/venues/added',
            status_code=200,
            responses={
                200 : status_codes["response_200"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def fetch_venues_added(
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(VENUES_COLLECTION))
):
    """
    API for venue managers to fetch venues added by them.

    This endpoint allows you to retrieve the venues created by the logged in user. 
    Access to this endpoint requires valid authorization credentials.
    """
    logger.info("'/venues/added' API is invoked.")
    try:
        logger.debug("Checking the venues created by the logged in user")
        response = await venues_managed_by_logged_in_venue_manager(credentials, collection)
        logger.info("Succcessfully retrieved the venues created by the logged in user")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/venues/added' : {exc}")
        handle_internal_server_error(exc)


@router.post('/venues/seats/block',
            status_code=200,
            responses={
                200 : status_codes["response_200"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def update_booked_seats(
    details: SeatBookedByVenueManager,
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(SHOW_SLOTS_COLLECTION))
):
    """
    API for venue managers to block seats that have been booked externally (e.g., at the venue or via a third-party system).
    These seats will be marked as booked in our database to prevent them from being shown as available to users on the platform.
    """

    logger.info("'/venues/seats/block' API is invoked.")
    try:
        logger.debug("Checking if the seat is already booked by any person")
        response = await update_seats_bookedby_venuemanager(credentials, collection, details)
        logger.info("Succcessfully retrieved information about the seats that are booked offline.")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/venues/seats/block' : {exc}")
        handle_internal_server_error(exc)
