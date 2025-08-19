import math
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger

def serialize_document(doc: dict) -> dict:
    """Serialize MongoDB documents to make them JSON serializable."""
    return {
        key: (str(value) if isinstance(value, ObjectId) else value)
        for key, value in doc.items()
    }

def exclude_fields(document: dict, fields_to_exclude: list) -> dict:
    """Remove specified fields from a document."""
    return {k: v for k, v in document.items() if k not in fields_to_exclude}

async def get_venue(collection: MongoDB, city: str, venue_name: str, page: int, page_size: int):
    logger.debug(f"Fetching venue(s) for city='{city}', venue_name='{venue_name}'")
    
    city = city.lower()
    city_query = {"location.city": city}

    # First check if the city exists
    venues_in_city = await collection.read_many(city_query)
    if not venues_in_city:
        logger.error(f"No venues found for city '{city}'")
        raise HTTPException(
            detail=response_content(
                404,
                "Venue(s) not found.",
                errors=[{"field": ["city"], "message": f"No venues found for city '{city}'"}]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )

    # If venue_name is provided, add to query and validate name too
    if venue_name:
        query = {**city_query, "name": venue_name}
        total_venues_count = await collection.count_documents(query)
        logger.debug("Total venues count matching the query: %d", total_venues_count)

        if total_venues_count == 0:
            logger.error(f"Venue name '{venue_name}' not found in city '{city}'")
            raise HTTPException(
                detail=response_content(
                    404,
                    "Venue not found.",
                    errors=[{"field": ["name"], "message": f"Venue '{venue_name}' not found in city '{city}'"}]
                ),
                status_code=status.HTTP_404_NOT_FOUND
            )

        total_pages = math.ceil(total_venues_count / page_size)
        if page > total_pages and total_venues_count > 0:
            raise HTTPException(
                status_code=400,
                detail=response_content(
                    400,
                    f"Page {page} does not exist. The maximum page is {total_pages}."
                )
            )

        skip = (page - 1) * page_size
        venues = await collection.read_many(query, skip=skip, limit=page_size)

        serialized_venues = [
            exclude_fields(serialize_document(venue), ["managed_by", "created_at", "last_updated_at"])
            for venue in venues
        ]

        return JSONResponse(
            content=response_content(
                status_code=200,
                message="Successfully retrieved the venue",
                data=serialized_venues
            ),
            status_code=status.HTTP_200_OK
        )

    # Else return all venues in the city (no venue_name)
    skip = (page - 1) * page_size
    venues = await collection.read_many(city_query, skip=skip, limit=page_size)
    response_list = [
        {"id": str(venue["_id"]), "name": venue["name"]}
        for venue in venues
    ]

    return JSONResponse(
        content=response_content(
            status_code=200,
            message="Successfully retrieved venue(s)",
            data=response_list
        ),
        status_code=status.HTTP_200_OK
    )
