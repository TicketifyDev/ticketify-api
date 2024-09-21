from fastapi import status
from fastapi.encoders import jsonable_encoder
from src.common.json_operations import create_json_response, read_json_data
from fastapi.responses import JSONResponse
from src.common.utils import response_content
from datetime import date, datetime


async def event_creation(username, request, event_response_file):
    title = request.title
    release_date = request.release_date

    existing_data = read_json_data(event_response_file)
    # Check if the title already exists
    for event_details in existing_data:
        if title in event_details:
            return JSONResponse(
                content=response_content(
                    409,
                    f"The title {title} already exists."
                ),
                status_code=status.HTTP_409_CONFLICT
            )
        
    data = jsonable_encoder(request)
    response = {}
    response=data

    # Check if the release date is less than or equal to todays date
    if release_date <= date.today():
        return JSONResponse(
            content=response_content(
                400,
                "The release date must be future date."
            ),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Add extra fields to the response data
    response['event_creation_date_and_time'] = datetime.now().isoformat()
    response['event_creation_request_status'] = "Under Review"
    response['created_by'] = username
    
    # Store the response in the JSON file
    create_json_response(title, response, event_response_file)
    return JSONResponse(
            content=response_content(
                202,
                "This event will be reviewed by our administrators for approval.",
                response
            ),
            status_code=status.HTTP_202_ACCEPTED
        )