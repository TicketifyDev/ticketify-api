from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from datetime import date, datetime, timezone


async def event_updation(credentials, title, request, collection: MongoDB):
    """
    Function to update an existing event in MongoDB.

    Args:
        credentials : For authorization and authentication of a user.
        title : The title of the event to be updated.
        request : The event details to update.
        collection : MongoDB collection to store event details.
    """
    
    token = credentials.credentials
    user_name, role = decode_access_token(token)

    required_roles = ['admin', 'organizer']
    validate_roles(required_roles, role)
    logger.debug("Checking if the required fields are given for updation.")
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                errors=[{"message": "At least one field is required for updation"}]
            )
        )
    
    logger.debug(f"Checking if the event '{title}' exists")
    title = title.lower()
    
    existing_event = await collection.read({"title": title})
    if not existing_event:
        logger.error(f"Event '{title}' not found in db.")
        raise HTTPException(
            detail=response_content(
                404,
                "Event not found.",
                errors=[{"field": ["title"], "message": f"Provided event {title} not found"}]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if existing_event["created_by"]!=user_name:
        raise HTTPException(
            detail=response_content(
                403,
                "You are not authorized to update this event."
            ),
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # Convert request to dictionary if it's a Pydantic model
    if hasattr(request, 'dict'):
        request_data = request.dict(exclude_unset=True)  # Exclude unset fields
    else:
        request_data = request

    # Prepare the update data
    update_data = {}
    
    for key, value in request_data.items():
        update_data[key] = value
    update_data = jsonable_encoder(update_data)
    # Merge existing event data with update data
    logger.debug("Merging the existing event data with the updated data.")
    
    current_time = datetime.now(timezone.utc).isoformat()
    for key, value in update_data.items():
        existing_event[key] = value
    existing_event["last_updated_by"] = user_name
    existing_event["last_updated_at"] = current_time
    logger.debug(f"Updating the event '{title}'")
    modified_count = await collection.update({"title": title}, existing_event)

    if modified_count == 0:
        logger.debug(f"No changes made for the event '{title}'")
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No changes made to the event."
        )

    logger.debug(f"The event '{title}' has been updated successfully")
    return JSONResponse(
        content=response_content(
            200,
            "The event has been successfully updated."
        ),
        status_code=status.HTTP_200_OK
    )
