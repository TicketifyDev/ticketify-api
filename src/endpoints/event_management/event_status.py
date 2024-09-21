from fastapi import status, HTTPException
from src.common.json_operations import read_json_data
from fastapi.responses import JSONResponse
from src.common.utils import response_content


async def event_status(event_response_file, title):
    existing_data = read_json_data(event_response_file)
        
    # Check if the title exists and get the event details
    if title in existing_data:
        event_status = existing_data[title]["event_creation_request_status"]
        return JSONResponse(
            content={
                "status_code": 200,
                "message": f"The status of the event is {event_status}"
            },
            status_code=status.HTTP_200_OK
        )
    else:
        raise HTTPException(
            detail=response_content(
                404,
                "Event not found.",
                errors=[
                    {
                        "field": ["title"],
                        "message": f"Provided event {title} not found"
                    }
                ]
            ),
            status_code=status.HTTP_404_NOT_FOUND
        )