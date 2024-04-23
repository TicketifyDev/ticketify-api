from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import status
from pathlib import Path
import json
from schemas.registration_schema import user_registration,organizer_registration
from common.create_json import create_response_json

router = APIRouter()

@router.post('/user-register',tags=["User Management"])
async def new_user_registration(deatils : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    return {"Registration" : "Successful"}


@router.post('/organizer-register',tags=["Event Management"],status_code=201)
async def new_organizer_registration(details : organizer_registration):
    """
    API for allowing new organizers to create accounts by providing organizer details.
    """
    
    current_directory= Path(__file__).parents[1]
    response_file="organizer_details.json"
    filename = current_directory / 'responses' / response_file

    # try:
    #     with open(filename,"r") as file:
    #         existing_data = json.load(file)

    name = details.name
    data = jsonable_encoder(details)

    create_response_json(name,data,filename)
    return JSONResponse(
        content={"message" : "Registration Successful"},
        status_code=status.HTTP_201_CREATED
    )
