from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timezone
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.endpoints.admin_management.generate_show_slots import generate_show_slots



def normalize_time(t: str) -> str:
    """
    Extracts only HH:MM from any ISO-like time string.
    Examples:
        13:23:00 -> 13:23
        18:36:10.166105+00:00 -> 18:36
        07:05Z -> 07:05
    """
    try:
        parts = t.split(":")
        return f"{parts[0]}:{parts[1]}"
    except Exception:
        return t  # fallback if something unexpected


def validate_screen_time_conflict(approved_events, venue_id, venue_name, screen_name, date_str, event_time):
    for approved in approved_events:
        for a_venue in approved.get("venues", []):
            if a_venue["venue_id"] == venue_id and a_venue["venue_name"] == venue_name:
                for a_screen in a_venue.get("screens", []):
                    if a_screen["screen_name"] == screen_name:
                        for a_date in a_screen.get("dates", []):
                            if a_date["date"] == date_str:  # same date
                                for a_time in a_date.get("times", []):
                                    approved_time = normalize_time(a_time)
                                    if approved_time == event_time:
                                        raise HTTPException(
                                            status_code=status.HTTP_400_BAD_REQUEST,
                                            detail=response_content(
                                                400,
                                                "Showtime conflict detected.",
                                                errors=[{
                                                    "field": "time",
                                                    "message": (
                                                        f"Conflict with existing event '{approved['title']}' "
                                                        f"on {date_str} at {event_time} "
                                                        f"in {venue_name}, {screen_name}."
                                                    )
                                                }]
                                            )
                                        )


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

    # ✅ Conflict validation (only if trying to approve)
    if review == "approve":
        for venue in event.get("venues", []):
            venue_id = venue.get("venue_id")
            venue_name = venue.get("venue_name")

            for screen in venue.get("screens", []):
                screen_name = screen.get("screen_name")

                approved_events = await event_collection.read_many(
                    {
                        "event_creation_request_status": "approved",
                        "venues.venue_id": venue_id,
                        "venues.venue_name": venue_name
                    },
                    limit=0
                )

                approved_events = [
                    ev for ev in approved_events
                    if any(
                        s["screen_name"] == screen_name
                        for v in ev.get("venues", [])
                        if v["venue_id"] == venue_id and v["venue_name"] == venue_name
                        for s in v.get("screens", [])
                    )
                ]
                logger.debug("Approved events fetched: %s", approved_events)

                # Normalize to list of dicts
                if approved_events and isinstance(approved_events, dict):
                    approved_events = [approved_events]

                if not isinstance(approved_events, list):
                    logger.error("Expected list of events, got: %s", type(approved_events))
                    approved_events = []

                # Compare times
                for date_entry in screen.get("dates", []):
                    date_str = date_entry.get("date")

                    for time_str in date_entry.get("times", []):
                        event_time = normalize_time(time_str)
                        # Check against approved events
                        validate_screen_time_conflict(approved_events, venue_id, venue_name, screen_name, date_str, event_time)

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
