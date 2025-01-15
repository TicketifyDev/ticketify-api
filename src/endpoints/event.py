from fastapi import APIRouter,HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pathlib import Path
from src.schemas.event_management_schema import create_event, update_event
from src.endpoints.event_management.event_creation import event_creation
from src.endpoints.event_management.event_status import event_status
from src.endpoints.event_management.event_deletion import event_deletion
from src.endpoints.event_management.event_updation import event_updation
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.common.db import MongoDB
from src.common.constants import EVENTS_COLLECTION
from src.common.logging_config import logger

router=APIRouter(prefix="/api/v1", tags=["Event Management"])
token = HTTPBearer()

collection = MongoDB(EVENTS_COLLECTION)

@router.post('/create-event',
             status_code=202,
             responses={
                202 : status_codes["response_202"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def add_new_event(request: create_event, credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    API for organizers to create new events (movies).
    """
    logger.info("'/create-event' API is invoked.")
    try:
        logger.debug(f"Event details received : {request.model_dump()}")
        response = await event_creation(credentials, request, collection)
        logger.info(f"Event '{request.title}' added successful.")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/create-event' : {exc}")
        handle_internal_server_error(exc)
    

@router.get('/event-status',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def check_event_status(title: str = Query(..., description="Title of the event to check the status"), credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    Check the status of an event based on its title.

    This endpoint allows you to retrieve the current status of an event. The event is identified by its title,
    which must be provided as a query parameter. Access to this endpoint requires valid authorization credentials.
    """
    logger.info("'/event-status' API is invoked.")
    try:
        logger.debug(f"Checking the event status for the event '{title}'")
        response = await event_status(credentials, collection, title)
        logger.info(f"Event status for the event '{title}' fetched successfully")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/event-status' : {exc}")
        handle_internal_server_error(exc)


@router.put('/update-event',
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
async def update_event(title: str, request: update_event, credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    API for organizers to update existing events (movies).
    """
    logger.info("'/update-event' API is invoked.")
    try:
        logger.debug(f"Starting the process of event updation for '{title}'.")
        response = await event_updation(credentials, title, request, collection)
        logger.info(f"Event '{title}' updated successfully")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/event-status' : {exc}")
        handle_internal_server_error(exc)
        

@router.delete('/delete-event',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def delete_event(title: str = Query(..., description="Title of the event to delete"), credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    Delete an event based on its title.

    This endpoint allows you to delete an event. The event is identified by its title,
    which must be provided as a query parameter. Access to this endpoint requires valid authorization credentials.
    """
    logger.info("'/delete-event' API is invoked.")
    try:
        logger.debug(f"Starting the process of event deletion for '{title}'.")
        response = await event_deletion(credentials, collection, title)
        logger.info(f"Event '{title}' deleted successfully")
        return response
    except HTTPException as http_exc :
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error occurred in '/delete-event' : {exc}")
        handle_internal_server_error(exc)

