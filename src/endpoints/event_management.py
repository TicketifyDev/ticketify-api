from fastapi import APIRouter,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
from schemas.event_management_schema import create_event
from common.create_json import create_response_json
from common.status_codes import status_codes
import json
from datetime import date

router=APIRouter()

current_directory= Path(__file__).parents[1]
response_file="event_add.json"
event_response_file = current_directory / 'responses' / response_file

@router.post('/create-event',
             tags=["Event Management"],
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
        raise HTTPException(detail = "The release date must be future date", status_code=403)
    
    # Store the response in JSON file
    create_response_json(title, data, event_response_file)
    return JSONResponse(content = response, status_code=201)  
    

