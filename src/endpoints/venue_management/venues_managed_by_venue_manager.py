from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.auth.auth_token import decode_access_token, validate_roles


async def venues_managed_by_logged_in_venue_manager(credentials, collection : MongoDB):
    """
    Function to fetch the venues created by the logged in user from DB.

    Args:
        credentials : For authorization and authentication of a user.
        collection : MongoDB collection to store venue details.
    """
    token = credentials.credentials
    user_name, role = decode_access_token(token)

    required_roles = ['admin','venue_manager']
    validate_roles(required_roles, role)
    logger.debug(f"Checking if any venue exists which are created by the '{user_name}'.")
    existing_events = await collection.read_many(
        {"managed_by": user_name},  # Filter by created_by field
        {"_id": 0, "name": 1}      # Projection: Only include 'name', exclude '_id'
    )

        
    # Check if venue exists
    if existing_events:
        logger.debug(f"Successfully retrieved the venues created by '{user_name}'")
        return JSONResponse(
            content=response_content(
                status_code=200,
                message="Successfully retrieved the venues.",
                data=existing_events
            ),
            status_code=status.HTTP_200_OK
        )
    else:
        logger.error(f"No venues were found that were created by the '{user_name}'.")
        raise HTTPException(
            detail=response_content(
                404,
                "No venues were found that were created by the logged-in user."
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )