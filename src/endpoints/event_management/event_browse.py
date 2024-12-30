from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from src.common.utils import response_content
from src.common.db import MongoDB
import math

async def event_browse(
    title : str,
    genre : str,
    location : str,
    sort_by : str,
    sort_order : str,
    page : int,
    page_size : int,
    collection : MongoDB
):
    """
    Function to browse events based on different parameters.
    """
    # Validate sort order
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Invalid sort_order parameter",
                errors=[{"field": "sort_order", "message": "Must be 'asc' or 'desc'"}],
            ),
        )
    order = ASCENDING if sort_order == "asc" else DESCENDING

    # Validate sort by
    if sort_by not in ["release_date", "duration", "title"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response_content(
                400,
                "Invalid sort_by parameter",
                errors=[{"field": "sort_by", "message": "Must be 'release_date' or 'duration'"}],
            ),
        )
    sort_criteria = [(sort_by, order)]

    # Query filters
    filters = {
        "event_creation_request_status": "approved",                        # Only approved events
        "release_date": {"$gte": datetime.today().strftime('%Y-%m-%d')},    # Upcoming or ongoing events
    }
    if title:
        filters["title"] = {
            "$regex": title, "$options": "i"         # Case-insensitive title search
        }                   
    if genre:
        filters["genre"] = {
            "$elemMatch": {"$regex": genre, "$options": "i"}    # Case-insensitive genre search
        }
    if location:
        filters["venues"] = {
            "$elemMatch": {"location": {"$regex": location, "$options": "i"}}   # Case-insensitive location search
        }

    # Fetch the total number of events based on the filter
    total_events_count = await collection.count_documents(filters)

    # Calculate total pages
    total_pages = math.ceil(total_events_count / page_size)

    # Prevent page overflow
    if page > total_pages and total_events_count > 0:
        raise HTTPException(
            status_code=400,
            detail=response_content(
                400, 
                f"Page {page} does not exist. The maximum page is {total_pages}."
            )
        )

    # Fetch events based on filters, skip/limit for pagination
    skip = (page - 1) * page_size
    events_data = await collection.read_many(
        filters,
        skip,
        page_size,
        sort_criteria
    )

    if not events_data:
        raise HTTPException(
            status_code=404,
            detail=response_content(
                404,
                "No events found matching the search criteria."
            )
        )
    
    # Only include necessary fields to display
    result = []
    for index,event in enumerate(events_data, start=1):
        result.append(
            {
                "id" : index,
                "name" : event["title"]
            }
        )

    # Return paginated response
    return JSONResponse(
        status_code=200,
        content=response_content(
            200,
            "Events fetched successfully.",
            {
                "events": result,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_events_count": total_events_count
            }
        )
    )

