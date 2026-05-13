from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer
from typing import Optional
from src.common.db import MongoDB, MongoDBCollectionProvider
from src.common.status_codes import status_codes
from src.common.constants import SHOW_SLOTS_COLLECTION, VENUES_COLLECTION
from src.common.utils import handle_internal_server_error
from src.common.logging_config import logger
from src.endpoints.ticket_management.ticket_availability import get_ticket_availability



router = APIRouter(prefix="/api/v1", tags=["Ticket Management"])
token = HTTPBearer()


@router.get("/tickets/availability",
            status_code=200,
            responses={
                200: status_codes["response_200"],
                400: status_codes["response_400"],
                401: status_codes["response_401"],
                403: status_codes["response_403"],
                404: status_codes["response_404"],
                500: status_codes["response_500"]
            })
async def tickets_availability(
    event_title: str = Query(description="Title of the event (movie)"),
    language: str = Query(description="Language of the event"),
    date: str = Query(description="Event date"),
    show_slot_id: Optional[str] = Query(None, description="Fetch detailed info for a specific event slot"),
    show_slots_collection: MongoDB = Depends(MongoDBCollectionProvider(SHOW_SLOTS_COLLECTION)),
    venue_collection: MongoDB = Depends(MongoDBCollectionProvider(VENUES_COLLECTION))
):
    """
    API to fetch the ticket availabilty details
    """
    logger.info("GET '/tickets/availability' API invoked.")

    try:
        response = await get_ticket_availability(show_slot_id, event_title, language, date, show_slots_collection, venue_collection)
        return response

    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        logger.error(f"Unexpected error in GET '/tickets/availability': {exc}")
        handle_internal_server_error(exc)
