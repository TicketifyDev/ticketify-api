from bson import ObjectId
from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.constants import CONFLICT_ERROR_CONSTANT
from src.common.db import MongoDB
from src.common.logging_config import logger
from datetime import date, datetime, timezone


async def event_creation(credentials, request, collection : MongoDB, venue_collection: MongoDB):
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
    logger.info("Starting event creation process")

    # Check if the title already exists
    existing_event = await collection.read({"title": title})
    logger.debug(f"Checking if event '{title}' already exists.")
    if existing_event:
        logger.error(f"Event '{title}' already exists.")
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
    # Venue validation
    for venue in data.get("venues", []):
        venue_id = venue.get("venue_id")
        venue_name = venue.get("venue_name")

        try:
            venue_object_id = ObjectId(venue_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response_content(
                    400,
                    f"Invalid venue_id format '{venue_id}'. Must be a valid ObjectId."
                )
            )
        # Check if venue_id exists in VENUE_COLLECTION
        db_venue = await venue_collection.read({"_id": venue_object_id})
        if not db_venue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response_content(
                    400,
                    f"Invalid venue_id '{venue_id}'. Venue not found."
                )
            )

        # Validate venue name
        if db_venue["name"] != venue_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response_content(
                    400,
                    f"Venue name mismatch for venue_id '{venue_id}'. Expected '{db_venue['name']}'."
                )
            )

        # Validate screen name
        db_screens = db_venue.get("screens", [])
        db_screen_map = {s["screen_name"] for s in db_screens}

        for screen in venue.get("screens", []):
            screen_name = screen.get("screen_name")

            if screen_name not in db_screen_map:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_content(
                        400,
                        f"Invalid screen_name '{screen_name}' for venue_id '{venue_id}'."
                    )
                )
    response = {}
    response=data

    # Check if the release date is less than or equal to todays date
    logger.debug("Checking if the release date is a future date")
    if release_date <= date.today():
        logger.error(f"The provided release date '{release_date} is not a future date")
        return JSONResponse(
            content=response_content(
                400,
                "The release date must be future date."
            ),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Add additional fields 
    current_time = datetime.now(timezone.utc).isoformat()
    # Add extra fields to the response data
    response['title'] = title
    response['event_creation_date_and_time'] = datetime.now().isoformat()
    response['event_creation_request_status'] = "under_review"
    response['created_by'] = username
    response["last_updated_by"] = username
    response["last_updated_at"] = current_time
    
    # Store the response in the DB
    logger.debug("Inserting event details into db.")
    await collection.create(response)
    logger.debug("Event details added to db")

    del response['_id']     # Remove _id from the response

    return JSONResponse(
        content=response_content(
            202,
            "This event will be reviewed by our administrators for approval.",
            response
        ),
        status_code=status.HTTP_202_ACCEPTED
    )