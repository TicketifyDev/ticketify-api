from fastapi import status, HTTPException
from src.common.utils import response_content
from fastapi.responses import JSONResponse
from bson import json_util
import json

async def event_information(collection, title):
    """ Function to fetch the complete information of an event"""
    
    titleName = title.lower()

    existing_event = await collection.read({"title": titleName})
    
    if not existing_event:
        raise HTTPException(
            detail=response_content(
                404,
                "Event not found.",
                errors=[{"field": ["title"], "message": f"The provided event '{title}' does not exists"}]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )
    else:
        del existing_event["_id"] 
        del existing_event["event_creation_request_status"]
        del existing_event["created_by"]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json.loads(json_util.dumps(response_content(
                200,
                "Successfully fetched event information.",
                existing_event
            )))
        )
        