from fastapi import status, HTTPException
from bson import ObjectId
from src.common.utils import handle_internal_server_error
from src.common.logging_config import logger
from src.common.db import MongoDB
from src.common.utils import response_content
from src.common.constants import VALIDATION_ERROR_CONSTANT
from fastapi.responses import JSONResponse

async def get_ticket_availability(show_slot_id, event_title, language, date, show_slots_collection: MongoDB, venue_collection: MongoDB):
    try:
        if show_slot_id:
            logger.debug(f"Fetching details for show_slot_id: {show_slot_id}")
            show_slot = await show_slots_collection.read({"_id": ObjectId(show_slot_id)})
            if not show_slot:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show slot not found")

            # Validate show slot status
            if show_slot.get("status") != "UPCOMING":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_content(
                        400,
                        VALIDATION_ERROR_CONSTANT,
                        errors=[{
                            "field": "show_slot_id",
                            "message": f"Show slot '{show_slot_id}' is not UPCOMING (current status: {show_slot.get('status')})."
                        }]
                    )
                )
            
            if event_title and event_title.lower() != show_slot.get("event_name", "").lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_content(
                        400,
                        VALIDATION_ERROR_CONSTANT,
                        errors=[{
                            "field": "event_title",
                            "message": f"Provided event_title '{event_title}' does not match the show slot."
                        }]
                    )
                )

            if language and language.lower() != show_slot.get("language", "").lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_content(
                        400,
                        VALIDATION_ERROR_CONSTANT,
                        errors=[{
                            "field": "language",
                            "message": f"Provided language '{language}' does not match the show slot."
                        }]
                    )
                )

            if date and date != show_slot.get("date"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_content(
                        400,
                        VALIDATION_ERROR_CONSTANT,
                        errors=[{
                            "field": "date",
                            "message": f"Provided date '{date}' does not match the show slot."
                        }]
                    )
                )

            response = {
                "show_slot_id": str(show_slot["_id"]),
                "event_name": show_slot.get("event_name"),
                "language": show_slot.get("language"),
                "date": show_slot.get("date"),
                "seating_layout": show_slot.get("seating_layout"),
                "seats_availability": show_slot.get("seats_availability"),
                "price_per_row": show_slot.get("price_per_row")
            }

            logger.info(f"Show slot '{show_slot_id}' details fetched successfully.")
            
            return JSONResponse(
                content=response_content(
                    200,
                    "Successfully fetched the show slot details",
                    response
                ),
                status_code=status.HTTP_200_OK
            )


        # Missing required filters
        if not (event_title and language and date):
            logger.warning("Missing mandatory filters: event_title, language, date.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response_content(
                    400,
                    "Please provide event_title, language, and date as query parameters."
                )
            )

        query = {
            "event_name": {"$regex": f"^{event_title}$", "$options": "i"},
            "language": language,
            "date": date,
            "status": "UPCOMING"
        }

        logger.debug(f"Show slot filter query: {query}")

        # Fetch all matching slots
        slots = await show_slots_collection.read_many(query, limit=1000)

        if not slots:
            logger.info("No show slots found for the given filters.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response_content(
                    404,
                    "No upcoming shows found for the given filters."
                )
            )

        venue_map = {}
        for slot in slots:
            venue_id = str(slot["venue_id"])

            if venue_id not in venue_map:
                venue = await venue_collection.read({"_id": ObjectId(venue_id)})
                if not venue:
                    logger.warning(f"Venue not found for venue_id: {venue_id}")
                    continue

                venue_map[venue_id] = {
                    "venue_id": venue_id,
                    "venue_name": venue["name"],
                    "venue_loc": venue["location"],
                    "features": venue.get("features", []),
                    "show_details": []
                }

            venue_map[venue_id]["show_details"].append({
                "show_slot_id": str(slot["_id"]),
                "time": slot.get("show_time"),
                "total_count": slot.get("total_seats", 0),
                "booked_count": slot.get("booked_count", 0)
            })

        response = list(venue_map.values())
        logger.info("Successfully fetched the venue and show details")

        return JSONResponse(
            content=response_content(
                200,
                "Successfully fetched the venue and show details",
                response
            ),
            status_code=status.HTTP_200_OK
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error in GET '/tickets/availability': {exc}")
        handle_internal_server_error(exc)
