from fastapi import APIRouter,HTTPException, Query, Security, Depends, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.schemas.event_management_schema import create_event
from src.schemas.event_management_schema import update_event as update_event_model
from src.endpoints.event_management.event_creation import event_creation
from src.endpoints.event_management.event_information import event_information
from src.endpoints.event_management.event_status import event_status
from src.endpoints.event_management.event_deletion import event_deletion
from src.endpoints.event_management.event_updation import event_updation
from src.endpoints.event_management.event_created_by_organizer import events_created_by_logged_in_user
from src.endpoints.event_management.event_browse import event_browse
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.common.db import MongoDB, MongoDBCollectionProvider
from src.common.constants import EVENTS_COLLECTION
from src.common.logging_config import logger

router=APIRouter(prefix="/api/v1", tags=["Event Management"])
token = HTTPBearer()

@router.post('/events',
             status_code=202,
             responses={
                202 : status_codes["response_202"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def add_new_event(
    request: create_event, 
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(EVENTS_COLLECTION))
):
    """
    API for organizers to create new events (movies).
    """
    logger.info("POST '/events' API is invoked.")
    try:
        logger.debug(f"Event details received : {request.model_dump()}")
        response = await event_creation(credentials, request, collection)
        logger.info(f"Event '{request.title}' added successfully.")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in POST '/events' : {exc}")
        handle_internal_server_error(exc)
    

@router.get('/events/status',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def check_event_status(
    title: str = Query(..., description="Title of the event to check the status"), 
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(EVENTS_COLLECTION))
):
    """
    API for organizers to check the status of an event created by them, based on the `title`.

    The event is identified by its `title`, which must be provided as a query parameter.\n 
    Access to this endpoint requires valid authorization credentials of an approved organizer.
    """
    logger.info("'/events/status' API is invoked.")
    try:
        logger.debug(f"Checking the event status for the event '{title}'")
        response = await event_status(credentials, collection, title)
        logger.info(f"Event status for the event '{title}' fetched successfully")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/events/status' : {exc}")
        handle_internal_server_error(exc)


@router.put('/events',
             status_code=202,
             responses={
                202 : status_codes["response_202"],
                204 : status_codes["response_204"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def update_event(
    title: str, 
    request: update_event_model, 
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(EVENTS_COLLECTION))
):
    """
    API for organizers to update existing events (movies).
    """
    logger.info(" PUT '/events' API is invoked.")
    try:
        logger.debug(f"Starting the process of event updation for '{title}'.")
        response = await event_updation(credentials, title, request, collection)
        logger.info(f"Event '{title}' updated successfully")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in PUT '/events' : {exc}")
        handle_internal_server_error(exc)
        

@router.delete('/events',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def delete_event(
    title: str = Query(..., description="Title of the event to delete"), 
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(EVENTS_COLLECTION))
):
    """
    API for organizers to Delete an event created by them, based on its title.

    This endpoint allows you to delete an event created. The event is identified by its title,
    which must be provided as a query parameter. Access to this endpoint requires valid authorization credentials.
    """
    logger.info("DELETE '/events' API is invoked.")
    try:
        logger.debug(f"Starting the process of event deletion for '{title}'.")
        response = await event_deletion(credentials, collection, title)
        logger.info(f"Event '{title}' deleted successfully")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in DELETE '/events' : {exc}")
        handle_internal_server_error(exc)


@router.get('/events/created',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def check_events_created(
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(EVENTS_COLLECTION))
):
    """
    API to fetch the title of the events that are created by the logged in user.

    This endpoint allows you to retrieve the events created by the logged in user. 
    Access to this endpoint requires valid authorization credentials.
    """
    logger.info("'/events/created' API is invoked.")
    try:
        logger.debug("Checking the events created by the logged in user")
        response = await events_created_by_logged_in_user(credentials, collection)
        logger.info("Succcessfully retrieved the events created by the logged in user")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/event-status' : {exc}")
        handle_internal_server_error(exc)

@router.get('/events/{title}',
            status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def details_of_an_event(
    title : str = Path(..., description="Title of the event to retrieve its complete details"),
    collection : MongoDB = Depends(MongoDBCollectionProvider(EVENTS_COLLECTION))
):
    """
    API to fetch complete information about an event, based on its title.
    """
    try:
        response = await event_information( collection, title)
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/event-status' : {exc}")
        handle_internal_server_error(exc)



@router.get('/events',
            status_code=200,
            responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def browse_events(
    title : Optional[str] = Query(None, description="Filter events by title"),
    genre : Optional[str] = Query(None, description="Filter events by genre(category)"),
    location : Optional[str] = Query(None, description="Filter events by venue(location)"),
    sort_by : Optional[str] = Query("release_date", description="Sort events by 'release_date' , 'duration' , 'title'"),
    sort_order : Optional[str] = Query("asc", description="Sort order : 'asc' or 'desc'"),
    page : int = Query(1, ge=1, description="Page number for pagination"),
    page_size : int = Query(10, ge=1, le=100, description="Number of events per page"),
    collection : MongoDB = Depends(MongoDBCollectionProvider(EVENTS_COLLECTION))
):
    """
    API for users to browse for upcoming and ongoing events.\n
    Users can filter by language, genre, and location, and sort results.
    """
    logger.info("GET '/events' API is invoked.")
    try:
        response = await event_browse(
            title,
            genre,
            location,
            sort_by,
            sort_order,
            page,
            page_size,
            collection
        )
        logger.info("Successfully fetched events based on filters")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in GET '/events' : {exc}")
        handle_internal_server_error(exc)