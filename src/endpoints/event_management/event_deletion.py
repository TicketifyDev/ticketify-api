from fastapi import status, HTTPException
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB


async def event_deletion(credentials, collection : MongoDB, title):
    """
    Function to delete an event in MongoDB.

    Args:
        credentials : For authorization and authentication of a user.
        collection : MongoDB collection.
        title : The event title that needs to be deleted.
    """
    
    token = credentials.credentials
    user_name, role = decode_access_token(token)

    required_roles = ['admin','organizer']
    validate_roles(required_roles, role)

    title = title.lower()

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
    

    if existing_event["created_by"]!=user_name:
        raise HTTPException(
            detail=response_content(
                403,
                "You are not authorized to delete this event."
            ),
            status_code=status.HTTP_403_FORBIDDEN
        )
    

    await collection.delete(existing_event)
    del existing_event['_id']

    return JSONResponse(
        content=response_content(
            200,
            f"The event {title} has been successfully removed.",
            title
        ),
        status_code=status.HTTP_200_OK
    )