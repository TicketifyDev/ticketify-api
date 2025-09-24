from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
import math

async def event_registration_requests(
        credentials : HTTPAuthorizationCredentials, 
        collection : MongoDB, 
        status : str,
        page : int, 
        page_size : int
    ):
    """
    Function to fetch paginated registration requests based on status submitted by Event Managers.
    """

    logger.info("Fetching event registration requests with status: %s, page: %d, page_size: %d", status, page, page_size)

    token = credentials.credentials
    username, role = decode_access_token(token)

    logger.debug(f"Decoded token for username '{username}' , role : '{role}'.")

    required_roles = ['admin']
    validate_roles(required_roles, role)

    # Define the query filter based on the 'status'
    query = {}
    if status:
        query["event_creation_request_status"] = status
        logger.debug("Query filter applied: %s", query)

    # Fetch the total number of organizers based on the filter
    total_events_count = await collection.count_documents(query)
    logger.debug("Total events count matching the query: %d", total_events_count)

    # Calculate total pages
    total_pages = math.ceil(total_events_count / page_size)
    logger.debug("Total pages calculated: %d", total_pages)

    # Prevent page overflow
    if page > total_pages and total_events_count > 0:
        raise HTTPException(
            status_code=400,
            detail=response_content(
                400, 
                f"Page {page} does not exist. The maximum page is {total_pages}."
            )
        )

    # Fetch organizers based on status, skip/limit for pagination
    skip = (page - 1) * page_size
    events_data = await collection.read_many(query, skip=skip, limit=page_size)

    # Only include necessary fields for reviewing
    registration_requests = []
    for event in events_data:
        # Convert _id if present
        event_id = str(event["_id"]) if "_id" in event else None

        # Convert venue_id for each venue if present
        venues = event.get("venues", [])
        for v in venues:
            if "venue_id" in v:
                v["venue_id"] = str(v["venue_id"])

        registration_requests.append({
                "id": event_id,
                "title": event.get('title'),
                "release_date": event.get('release_date'),
                "duration": event.get('duration'),
                "languages": event.get('languages'),
                "genre": event.get('genre'),
                "cast": event.get('cast'),
                "crew": event.get('crew'),
                "venues": venues,
                "event_creation_date_and_time": event.get('event_creation_date_and_time'),
                "event_creation_request_status": event.get('event_creation_request_status')
            })
        
    # Convert the enum status value to a user-friendly message format
    status_message = status.value.replace("_", " ").title()  

    logger.debug("Successfully fetched event registration requests with status: %s", status)

    # Return paginated response
    return JSONResponse(
        status_code=200,
        content=response_content(
            200,
            f"Successfully retrieved event registration requests that are '{status_message}'." if status else 
            "Successfully retrieved all event registration requests.",
            {
                "requests": registration_requests,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_events_count": total_events_count
            }
        )
    )