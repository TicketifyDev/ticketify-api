from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.constants import CONFLICT_ERROR_CONSTANT
from src.common.db import MongoDB
from datetime import date, datetime


async def event_creation(credentials, request, collection : MongoDB):
    """
    Function to add a new event in MongoDB.

    Args:
        credentials : For authorization and authentication of a user.
        request : The event details of the event to be added.
        collection : MongoDB collection to store event details.
    """
    
    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['admin','organizer']
    validate_roles(required_roles, role)

    title = request.title.lower()
    release_date = request.release_date

    # Check if the title already exists
    existing_event = await collection.read({"title": title})
    if existing_event:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "title", 
                        "message": f"The title '{title}' already exists."
                    }
                ]
            )
        )

        
    data = jsonable_encoder(request)
    response = {}
    response=data

    # Check if the release date is less than or equal to todays date
    if release_date <= date.today():
        return JSONResponse(
            content=response_content(
                400,
                "The release date must be future date."
            ),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Add extra fields to the response data
    response['title'] = title
    response['event_creation_date_and_time'] = datetime.now().isoformat()
    response['event_creation_request_status'] = "under_review"
    response['created_by'] = username
    
    # Store the response in the DB
    await collection.create(response)

    del response['_id']     # Remove _id from the response

    return JSONResponse(
        content=response_content(
            202,
            "This event will be reviewed by our administrators for approval.",
            response
        ),
        status_code=status.HTTP_202_ACCEPTED
    )