from fastapi import status, HTTPException
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from datetime import datetime, timezone
from bson import ObjectId

async def venue_deletion(credentials, venue_id, collection: MongoDB):
    """
    Function to delete a Venue.
    """
    
    token = credentials.credentials
    user_name, role = decode_access_token(token)

    required_roles = ['venue_manager']
    validate_roles(required_roles, role)

    
    logger.debug(f"Checking if the venue '{venue_id}' exists for deletion")

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

    org_venue_id = ObjectId(venue_id)
    
    existing_venue = await collection.read({"_id": ObjectId(org_venue_id)})
    if not existing_venue:
        logger.error(f"Venue with ID'{org_venue_id}' not found in database.")
        raise HTTPException(
            detail=response_content(
                404,
                "Venue not found.",
                errors=[{"field": ["venue_id"], "message": f"Provided venue with id'{org_venue_id}' not found"}]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if existing_venue["managed_by"] != user_name:
        raise HTTPException(
            detail=response_content(
                403,
                "You are not authorized to delete this Venue."
            ),
            status_code=status.HTTP_403_FORBIDDEN
        )

    current_time = datetime.now(timezone.utc).isoformat()
    update_data = {
        "is_active": False,
        "last_updated_at": current_time,
    }

    modified_count = await collection.update({"_id": org_venue_id}, update_data)

    if modified_count == 0:
        logger.debug(f"No changes made for the venue '{org_venue_id}'")
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No changes made to the venue."
        )

    logger.debug(f"The Venue '{org_venue_id}' has been deleted successfully")


    return JSONResponse(
        content=response_content(
            200,
            "Venue deleted successfully."
        ),
        status_code=status.HTTP_200_OK
    )