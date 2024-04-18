from fastapi import FastAPI
from pydantic import BaseModel
from schemas.event_manage import create_event
from fastapi import APIRouter, Response, Query, status
from fastapi.encoders import jsonable_encoder
from pathlib import Path
import json
from fastapi.responses import JSONResponse

router1=APIRouter(prefix="/event_management",
                 tags=["Events"])

current_directory= Path(__file__).parents[1]
response_file="event_add.json"
event_response_file = current_directory / 'responses' / response_file

@router1.post('/create_event')
async def add_event(request: create_event):
    title = request.title
    response = {}
    response[title]=jsonable_encoder(request)
    with open(event_response_file,'w') as resp_file:
        json.dump(response,resp_file,indent=4)
    return JSONResponse(content = response, status_code=201)
