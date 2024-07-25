from fastapi import APIRouter,HTTPException,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
from schemas.event_management_schema import create_event
from common.json_operations import create_json_response, read_json_data
from common.status_codes import status_codes
from common.utils import response_content
import traceback
import json
from datetime import date

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
    
    title = request.title
    release_date = request.release_date
    # Check if the file is empty or file doesn't exist
    try : 
        with open(event_response_file, "r") as file:
            existing_data = json.load(file)
        # Check if the title already exists
        for event_details in existing_data:
            if title in event_details:
                return JSONResponse(status_code=400, content = f"The title {title} already exists, please use /update-event to modify the event")
            
    except Exception:
        pass
    
    data = jsonable_encoder(request)
    response = {}
    response[title]=data

    # Check if the release date is less than or equal to todays date
    if release_date <= date.today():
        raise HTTPException(detail = "The release date must be future date", status_code=400)
    
    # Store the response in JSON file
    create_json_response(title, data, event_response_file)
    return JSONResponse(content = response, status_code=201)  



@router.get('/check-event-status',
             status_code=201,
             responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def check_event_status(title: str):
    try:
        existing_data = read_json_data(event_response_file)
        
        # Check if the title exists and get the event details
        for event_details in existing_data:
            if title in event_details:
                # Assuming event_details[title] contains additional fields
                event_status = event_details[title]["event_creation_request_status"]
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
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{exc}' : {exception_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_content(
                500,
                "An unexpected error occurred. Please try again later.",
                errors=[
                    {
                        "field": "general", 
                        "message": str(exc)
                    }
                ]
            )
        )
