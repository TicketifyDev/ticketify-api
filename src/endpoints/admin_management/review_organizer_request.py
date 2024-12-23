from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timezone
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.db import MongoDB

async def review_organizer_registration_request(
        username : str,
        review : str,
        organizers_collection : MongoDB,
        credentials : HTTPAuthorizationCredentials
):
    """
    Function to review an organizer's request and approve/reject it.
    """
    token = credentials.credentials
    _, role = decode_access_token(token)

    required_roles = ['admin']
    validate_roles(required_roles, role)

    # Find the organizer in the database by username
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
    
    # Ensure the organizer is still under review
    if organizer["registration_status"] != "under_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Organizer already reviewed.",
                errors=[
                    {
                        "field": "registration_status", 
                        "message": "Status is not 'under_review'."
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
        "reviewed_at": datetime.now(timezone.utc).isoformat()
    }
    
    updated_count = await organizers_collection.update({"user_name": username}, update_data)

    if updated_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organizer's registration status."
        )

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
