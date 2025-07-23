from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.constants import VALIDATION_ERROR_CONSTANT
from src.common.db import MongoDB
from src.common.logging_config import logger

async def create_venue(credentials, data, collection : MongoDB):
    """
    Function to add a new venue in MongoDB.

    Args:
        credentials : For authorization and authentication of user(venue manager).
        data : The venue details of the venue to be added.
        collection : MongoDB collection to store venue details.
    """

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['venue_manager']
    validate_roles(required_roles, role)

    logger.info("Starting venue creation process")

    # Validate that at least one screen exists
    if len(data.screens) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                VALIDATION_ERROR_CONSTANT,
                errors=[{
                    "field": "screens",
                    "message": "At least one screen must be provided."
                }]
            )
        )

    venue_data = jsonable_encoder(data)

    # Add additional fields 
    current_time = datetime.now(timezone.utc).isoformat()
    venue_data["managed_by"] = username
    venue_data["created_at"] = current_time
    venue_data["last_updated_at"] = current_time
    venue_data["is_active"] = True

    # Store the data in the DB
    logger.debug("Inserting venue details into db.")
    await collection.create(venue_data)
    logger.debug("Venue details added to db")

    venue_data["id"] = str(venue_data["_id"])
    del venue_data["_id"]

    return JSONResponse(
        content=response_content(
            201,
            "Venue added successfully.",
            venue_data
        ),
        status_code=status.HTTP_201_CREATED
    )