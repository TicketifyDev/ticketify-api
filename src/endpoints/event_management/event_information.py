from src.common.db import MongoDB
from fastapi import status, HTTPException
from src.common.utils import response_content
from src.auth.auth_token import decode_access_token, validate_roles


async def event_information(credentials, collection, title):
    """ Function to fetch the complete information of an event"""
    
    token = credentials.credentials
    _, role = decode_access_token(token)

    required_roles = ['organizer','user']
    validate_roles(required_roles, role)

    titleName = title.lower()

    existing_event = await collection.read({"title": titleName})
    
    if not existing_event:
        raise HTTPException(
            detail=response_content(
                404,
                "Event not found.",
                errors=[{"field": ["title"], "message": f"The provided event '{title}' does not exists"}]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )
    else:
        del existing_event["_id"] 
        del existing_event["event_creation_request_status"]
        del existing_event["created_by"]
        return existing_event
        