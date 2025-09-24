from src.common.logging_config import logger
from src.common.db import MongoDB
from src.common.constants import SHOW_SLOTS_COLLECTION, VENUES_COLLECTION
from datetime import datetime, timezone, timedelta
from bson import ObjectId

venues_collection = MongoDB(VENUES_COLLECTION)
show_slots_collection = MongoDB(SHOW_SLOTS_COLLECTION)

async def generate_show_slots(
        title,
        event
):
    logger.info(f"Generating show slots for approved event '{title}'")

    event_oid = ObjectId(event.get("_id"))
    duration_minutes = event.get("duration", 180)  # fallback to 3h
    languages = event.get("languages", [])

    for venue_ref in event.get("venues", []):
        venue_oid = ObjectId(venue_ref["venue_id"])
        venue_name = venue_ref["venue_name"]
        venue = await venues_collection.read({"_id": venue_oid})
        if not venue:
            logger.warning(f"Venue {venue_oid} not found, skipping...")
            continue

        for screen_ref in venue_ref.get("screens", []):
            screen_name = screen_ref["screen_name"]

            # find full screen data from venue.screens[]
            screen = next((s for s in venue["screens"] if s["screen_name"] == screen_name), None)
            if not screen:
                logger.warning(f"Screen {screen_name} not found in venue {venue['name']}, skipping...")
                continue

            rows = screen["seating_layout"]["rows"]
            cols = screen["seating_layout"]["columns"]

            # build seat ids like A1..A15, B1..B15, ...
            seats_availability = {}
            for r in range(rows):
                row_char = chr(65 + r)  # A, B, C...
                for c in range(1, cols + 1):
                    seats_availability[f"{row_char}{c}"] = "available"

            # build price_per_row from pricing.zones
            price_per_row = {}
            for zone in screen["pricing"]["zones"]:
                for row_char in zone["rows"]:
                    price_per_row[row_char] = zone["price"]

            for date_block in screen_ref.get("dates", []):
                show_date = date_block["date"]
                for show_time in date_block["times"]:
                    for lang in languages:
                        # compute start/end time
                        start_dt = datetime.fromisoformat(f"{show_date}T{show_time}")
                        end_dt = start_dt + timedelta(minutes=duration_minutes)

                        show_slot_doc = {
                            "event_id": event_oid,
                            "event_name": title,
                            "venue_id": venue_oid,
                            "venue_name": venue_name,
                            "screen_name": screen_name,
                            "screen_type": ", ".join(screen.get("features", [])),
                            "date": show_date,
                            "language": lang,
                            "show_time": show_time,
                            "start_time": start_dt.isoformat(),
                            "end_time": end_dt.isoformat(),
                            "seating_layout": screen["seating_layout"],
                            "seats_availability": seats_availability,
                            "price_per_row": price_per_row,
                            "booked_count": 0,
                            "status": "UPCOMING",
                            "created_from_event": True,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        }

                        # prevent duplication if already exists
                        exists = await show_slots_collection.read({
                            "event_id": event_oid,
                            "event_name": title,
                            "venue_id": venue_oid,
                            "screen_name": screen_name,
                            "date": show_date,
                            "language": lang,
                            "show_time": show_time
                        })

                        if exists:
                            logger.debug(f"Slot already exists for {screen_name} {show_date} {show_time} {lang}, skipping...")
                            continue

                        await show_slots_collection.create(show_slot_doc)
                        logger.info(f"Created show slot: {screen_name} {show_date} {show_time} {lang}")