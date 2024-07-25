from fastapi import APIRouter,HTTPException,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
from schemas.event_management_schema import create_event
from common.json_operations import create_json_response, read_json_data
from common.status_codes import status_codes
from common.utils import response_content
import traceback
from datetime import date, datetime

router=APIRouter(tags=["Event Management"])

current_directory= Path(__file__).parents[1]
response_file="event_add.json"
event_response_file = current_directory / 'responses' / response_file

@router.post('/create-event',
             status_code=201,
             responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def add_new_event(request: create_event):
    """
    API for organizers to create new events (movies).
    """
    try:
        title = request.title
        release_date = request.release_date
        # Check if the file is empty or file doesn't exist
        try : 
            existing_data = read_json_data(event_response_file)
            # Check if the title already exists
            for event_details in existing_data:
                if title in event_details:
                    return JSONResponse(
                        content=response_content(
                            400,
                            f"The title {title} already exists, please use /update-event to modify the event"
                        ),
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
        except Exception:
            pass
        
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
        
        # Store the response in the JSON file
        create_json_response(title, response, event_response_file)
        return JSONResponse(
                content=response_content(
                    201,
                    "This event will be reviewed by our administrators for approval.",
                    response
                ),
                status_code=status.HTTP_201_CREATED
            )
    except Exception as e:
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_content(
                500,
                "An unexpected error occurred. Please try again later."
            )
        )
    

