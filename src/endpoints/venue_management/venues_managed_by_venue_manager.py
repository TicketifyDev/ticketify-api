from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.auth.auth_token import decode_access_token, validate_roles
from bson import ObjectId

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
    

async def update_seats_bookedby_venuemanager(credentials, collection: MongoDB, details):
    """
    Function that allows venue managers to update offline sold tickets 
    by marking seats as 'booked_external'.

    Args:
        credentials : For authorization and authentication of a user.
        collection : MongoDB collection where show slots are stored.
        details : request body (SeatBookedByVenueManager model)
    """
    # Step 1: Authorization
    token = credentials.credentials
    user_name, role = decode_access_token(token)

    required_roles = ['venue_manager']
    validate_roles(required_roles, role)
    logger.debug(f"Venue manager '{user_name}' is requesting to block seats.")

    # Step 2: Extract fields from validated details
    data = details.dict() if hasattr(details, "dict") else details
    show_slot_id = data["show_slot_id"]

    # Validate ObjectId format before using it
    show_slot_id =show_slot_id.strip().lower()
    if not ObjectId.is_valid(show_slot_id):
        logger.error(f"Invalid show_slot_id format: '{show_slot_id}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Invalid `show_slot_id` format.",
                errors=[{"field": "show_slot_id", "message": "Must be a 24-character hex string"}]
            )
        )
    seats_to_block = data["seats"]

    slot_id = ObjectId(show_slot_id)
    
    show_slot = await collection.read({"_id": ObjectId(slot_id)})
    if not show_slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response_content(404, "Show slot not found.")
            )

    # Step 4: Validate show slot status
    slot_status = show_slot.get("status")
    if slot_status not in ["UPCOMING", "RUNNING"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                f"Cannot update seats for {slot_status} show slots."
            )
        )

    # Step 5: Validate seat IDs exist in layout
    seats_availability = show_slot.get("seats_availability", {})
    invalid_seats = [seat for seat in seats_to_block if seat not in seats_availability]
    if invalid_seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Invalid seat IDs",
                errors=[{
                    "field": "seats",
                    "message": f"Invalid seat IDs {invalid_seats}"
                }]
            )
        )

    # Step 6: Check for conflicts (already booked by users)
    already_booked = [
        seat for seat in seats_to_block
        if seats_availability.get(seat) not in ["available"]
    ]
    
    if already_booked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                "Seat(s) already booked",
                errors=[{
                    "field": "seats",
                    "message": f"Seat(s) {already_booked} already booked"
                }]
            )
        )

    event_obj_id = ObjectId(data["event_id"])
    venue_obj_id = ObjectId(data["venue_id"])
    

    # Build filter for event, venue, screen, date, show_time
    filter_query = {
        "_id": slot_id,
        "event_id": event_obj_id,
        "venue_id": venue_obj_id,
        "screen_name": data["screen_name"],
        "date": data["date"],
        "show_time": data["show_time"]
    }

    show_slot = await collection.collection.find_one(filter_query)

    if not show_slot:
        logger.error(
            f"No show slot found for event_id={data['event_id']}, venue_id={data['venue_id']}, "
            f"screen_name={data['screen_name']}, date={data['date']}, show_time={data['show_time']}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response_content(
                404,
                "Show slot with the specified combination does not exist."
            )
        )
    
    newly_blocked = 0
    # Step 7: Mark requested seats as booked_external
    for seat in seats_to_block:
        if seats_availability.get(seat) == "available":
            seats_availability[seat] = "booked_external"
            newly_blocked += 1

    # Step 8: Update booked_count accurately
    total_booked = sum(
        1 for status in seats_availability.values() if status != "available"
    )

    result = await collection.collection.update_one(
        {"_id": slot_id},
        {"$set": {
            "seats_availability": seats_availability,
            "booked_count": total_booked
        }}
    )

    if result.modified_count == 0:
        logger.warning(f"No document updated for show_slot_id={show_slot_id}")
    logger.info(
        f"Venue manager '{user_name}' successfully blocked seats {seats_to_block} for show {show_slot_id}."
    )

    # Step 10: Return success response
    return JSONResponse(
        content=response_content(
            200,
            "Seats blocked successfully",
            data={
                "blocked_seats": seats_to_block,
                "current_booked_count":newly_blocked,
                "total_booked_count": total_booked
            }
        ),
        status_code=status.HTTP_200_OK
    )