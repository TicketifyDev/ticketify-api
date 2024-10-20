from fastapi import status, HTTPException
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB
from datetime import date, datetime


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
    _, role = decode_access_token(token)

    required_roles = ['admin', 'organizer']
    validate_roles(required_roles, role)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                errors=[{"message": "At least one field is required for updation"}]
            )
        )
    
    existing_event = await collection.read({"title": title})
    if not existing_event:
        raise HTTPException(
            detail=response_content(
                404,
                "Event not found.",
                errors=[{"field": ["title"], "message": f"Provided event {title} not found"}]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Convert request to dictionary if it's a Pydantic model
    if hasattr(request, 'dict'):
        request_data = request.dict(exclude_unset=True)  # Exclude unset fields
    else:
        request_data = request

    # Prepare the update data
    update_data = {}
    
    for key, value in request_data.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            # Convert date to datetime if necessary
            update_data[key] = datetime(value.year, value.month, value.day)
        else:
            update_data[key] = value

    # Merge existing event data with update data
    for key, value in update_data.items():
        existing_event[key] = value

    modified_count = await collection.update({"title": title}, existing_event)

    if modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No changes made to the event."
        )

    return JSONResponse(
        content=response_content(
            200,
            "The event has been successfully updated."
        ),
        status_code=status.HTTP_200_OK
    )
