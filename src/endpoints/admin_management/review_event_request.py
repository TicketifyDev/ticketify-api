from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timezone
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.endpoints.admin_management.generate_show_slots import generate_show_slots

async def review_event_registration_request(
        title : str,
        review : str,
        event_collection : MongoDB,
        credentials : HTTPAuthorizationCredentials,
        rejection_reason : str
):
    """
    Function to review an event's request and approve/reject it.
    If status is approved, auto-generate show slots.
    """

    logger.info("Reviewing event registration request for title: %s, action: %s", title, review)

    token = credentials.credentials
    logged_in_user_name, role = decode_access_token(token)

    logger.debug(f"Decoded token for username '{logged_in_user_name}' , role : '{role}'.")

    required_roles = ['admin']
    validate_roles(required_roles, role)

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

    # Find the event in the database by title
    logger.debug("Fetching event with title: %s", title)
    event = await event_collection.read({"title": title})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response_content(
                404,
                "Event not found.",
                errors=[
                    {
                        "field": "title", 
                        "message": f"No event found with the title '{title}'."
                    }
                ]
            )
        )
    
    # Ensure the event is not approved
    if event["event_creation_request_status"] == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Event already reviewed.",
                errors=[
                    {
                        "field": "event_creation_request_status", 
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
        "event_creation_request_status": review_status,
        "rejection_reason": rejection_reason if rejection_reason is not None else "",
        "reviewed_by": logged_in_user_name,
        "reviewed_at": datetime.now(timezone.utc).isoformat()
    }
    
    logger.debug("Updating event %s with data: %s", title, update_data)

    updated_count = await event_collection.update({"title": title}, update_data)

    if updated_count == 0:
        logger.error("Failed to update event's registration status for title: %s", title)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event's registration status."
        )

    logger.debug("Successfully %s event registration for title: %s", review_status, title)

    # If event approved, generate show slots
    if review.lower() == "approve":
        await generate_show_slots(title, event)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_content(
            200,
            f"'{review_status.upper()}' Event successfully.",
            data={
                "title": title,
                "event_creation_request_status": review_status
            }
        )
    )
