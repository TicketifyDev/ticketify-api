from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
from schemas.event_management_schema import create_event
import json

router=APIRouter(tags=["Event Management"])

current_directory= Path(__file__).parents[1]
response_file="event_add.json"
event_response_file = current_directory / 'responses' / response_file

@router.post('/create-event')
async def add_new_event(request: create_event):
    """
    API for organizers to create new events (movies).
    """

    title = request.title
    response = {}
    response[title]=jsonable_encoder(request)
    with open(event_response_file,'w') as resp_file:
        json.dump(response,resp_file,indent=4)
    return JSONResponse(content = response, status_code=201)

