from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from datetime import date, datetime, timezone
from bson import ObjectId

async def venue_updation(credentials, venue_id, details, collection: MongoDB):
    """
    Function to update an existing event in MongoDB.

    Args:
        credentials : For authorization and authentication of a venue manager.
        venue_id : The id of the venue to be updated.
        details : The venue details to update.
        collection : MongoDB collection to store venue details.
    """
    
    token = credentials.credentials
    user_name, role = decode_access_token(token)

    required_roles = ['venue_manager']
    validate_roles(required_roles, role)

    logger.debug("Checking if the required fields are given for updation.")
    if not details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                errors=[{"message": "At least one field is required for updation"}]
            )
        )
    
    logger.debug(f"Checking if the venue '{venue_id}' exists")

    # Validate ObjectId format before using it
    venue_id = venue_id.strip().lower()
    if not ObjectId.is_valid(venue_id):
        logger.error(f"Invalid venue_id format: '{venue_id}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Invalid `venue_id` format.",
                errors=[{"field": "venue_id", "message": "Must be a 24-character hex string"}]
            )
        )

    venue_oid = ObjectId(venue_id)
    
    existing_venue = await collection.read({"_id": ObjectId(venue_oid)})
    if not existing_venue:
        logger.error(f"Venue '{venue_oid}' not found in db.")
        raise HTTPException(
            detail=response_content(
                404,
                "Venue not found.",
                errors=[{"field": ["venue_id"], "message": f"Provided venue '{venue_oid}' not found"}]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if existing_venue["managed_by"] != user_name:
        raise HTTPException(
            detail=response_content(
                403,
                "You are not authorized to update this Venue."
            ),
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    update_data = details.dict(exclude_unset=True)

    current_time = datetime.now(timezone.utc).isoformat()
    update_data["last_updated_at"] = current_time

    logger.debug(f"Updating venue with ID '{venue_oid}' and data: {update_data}")

    modified_count = await collection.update({"_id": ObjectId(venue_oid)}, update_data)

    if modified_count == 0:
        logger.debug(f"No changes made for the venue '{venue_oid}'")
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No changes made to the venue."
        )

    updated_venue = await collection.read({"_id": ObjectId(venue_oid)})
    updated_venue["id"] = str(updated_venue["_id"])
    del updated_venue["_id"]

    logger.debug(f"The Venue '{venue_oid}' has been updated successfully")

    return JSONResponse(
        content=response_content(
            200,
            "Venue updated successfully.",
            updated_venue
        ),
        status_code=status.HTTP_200_OK
    )