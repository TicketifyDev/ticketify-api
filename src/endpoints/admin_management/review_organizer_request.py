from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timezone
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger

async def review_organizer_registration_request(
        username : str,
        review : str,
        organizers_collection : MongoDB,
        credentials : HTTPAuthorizationCredentials,
        rejection_reason : str
):
    """
    Function to review an organizer's request and approve/reject it.
    """

    logger.info("Reviewing organizer registration request for username: %s, action: %s", username, review)

    token = credentials.credentials
    logged_in_user_name, role = decode_access_token(token)

    logger.debug(f"Decoded token for username '{logged_in_user_name}' , role : '{role}'.")

    required_roles = ['admin']
    validate_roles(required_roles, role)
    print("reason :", rejection_reason)
    if review == "reject" and not rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Missing Field.",
                errors=[
                    {
                        "field": "rejection_reason", 
                        "message": "Reason is required when review is set to 'reject'."
                    }
                ]
            )
        )

    # Find the organizer in the database by username
    logger.debug("Fetching organizer with username: %s", username)
    organizer = await organizers_collection.read({"user_name": username})
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response_content(
                404,
                "Organizer not found.",
                errors=[
                    {
                        "field": "username", 
                        "message": f"No organizer found with the username '{username}'."
                    }
                ]
            )
        )
    
    # Ensure the organizer is not approved
    if organizer["registration_status"] == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Organizer already reviewed.",
                errors=[
                    {
                        "field": "registration_status", 
                        "message": "Status is already 'approved'."
                    }
                ]
            )
        )
    
    # Update the registration status and add a review timestamp
    if review == "approve":
        review_status = "approved"
    elif review == "reject":
        review_status = "rejected"

    update_data = {
        "registration_status": review_status,
        "rejection_reason": rejection_reason if rejection_reason is not None else "",
        "reviewed_by": logged_in_user_name,
        "reviewed_at": datetime.now(timezone.utc).isoformat()
    }
    
    logger.debug("Updating organizer %s with data: %s", username, update_data)

    updated_count = await organizers_collection.update({"user_name": username}, update_data)

    if updated_count == 0:
        logger.error("Failed to update organizer's registration status for username: %s", username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organizer's registration status."
        )

    logger.debug("Successfully %s organizer registration for username: %s", review_status, username)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_content(
            200,
            f"'{review_status.upper()}' Organizer successfully.",
            data={
                "username": username,
                "registration_status": review_status
            }
        )
    )
