from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.auth.auth_token import decode_access_token, validate_roles


async def event_status(credentials, collection : MongoDB, title):
    """
    Function to fetch the event status from DB.

    Args:
        credentials : For authorization and authentication of a user.
        collection : MongoDB collection to store event details.
        title : Title of the event
    """
    token = credentials.credentials
    _, role = decode_access_token(token)

    required_roles = ['admin','organizer']
    validate_roles(required_roles, role)
    logger.debug(f"Checking if the '{title}' exists in db.")
    existing_event = await collection.read({"title": title})
        
    # Check if the title exists and get the status
    if existing_event:
        logger.debug(f"Fetching the status of the event '{title}'")
        event_status = existing_event["event_creation_request_status"]
        return JSONResponse(
            content={
                "status_code": 200,
                "message": f"The status of the event is {event_status}"
            },
            status_code=status.HTTP_200_OK
        )
    else:
        logger.error(f"Provided event '{title}' not found in db.")
        raise HTTPException(
            detail=response_content(
                404,
                "Event not found.",
                errors=[
                    {
                        "field": ["title"],
                        "message": f"Provided event {title} not found"
                    }
                ]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )