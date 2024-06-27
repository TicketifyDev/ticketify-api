from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from schemas.registration_schema import user_registration,organizer_registration
from common.json_operations import create_json_response, read_json_data
from common.status_codes import status_codes
from common.utils import hash_password

router = APIRouter()

@router.post('/user-register',tags=["User Management"])
async def new_user_registration(deatils : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    return {"Registration" : "Successful"}


@router.post('/organizer-register',
             tags=["Organizer Management"],
             status_code=201,
             responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                }
            )

async def new_organizer_registration(details : organizer_registration):
    """
    API for allowing new organizers to create accounts by providing organizer details.
    """
    
    current_directory= Path(__file__).parents[1]
    response_file="organizer_details.json"
    filename = current_directory / 'responses' / response_file

    existing_data = read_json_data(filename)

    for organizers_data in existing_data.values():
        # Check if username already exists
        if details.user_name == organizers_data["user_name"]:         
            raise HTTPException(
                status_code=400, 
                detail=f"The username '{details.user_name}' is already taken."
                )

        # Check if email already exists
        if details.email == organizers_data["email"]:              
            raise HTTPException(
                status_code=400, 
                detail=f"The email '{details.email}' is already registered."
                )

        # Check if organization name already exists
        if details.organization_details.organization_name == organizers_data["organization_details"]["organization_name"]: 
            raise HTTPException(
                status_code=400, 
                detail=f"The organization with the name '{details.organization_details.organization_name}' already exists."
                )

        # Check if organization PAN  already exists
        if details.organization_details.organization_pan_card_number == organizers_data["organization_details"]["organization_pan_card_number"]:         
            raise HTTPException(
                status_code=400, 
                detail=f"The PAN card number '{details.organization_details.organization_pan_card_number}' is already associated with another organization. Please verify the details and try again."
                )
    
    # Hash the password
    hashed_password = hash_password(details.password)

    username = details.user_name
    data = jsonable_encoder(details)
    data["password"] = hashed_password

    # Store the response in JSON file
    create_json_response(username,data,filename)
    return JSONResponse(
        content={"message" : "Registration Successful"},
        status_code=201
    )
