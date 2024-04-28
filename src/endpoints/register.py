from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from schemas.registration_schema import user_registration,organizer_registration
from common.create_json import create_response_json
from common.status_codes import status_codes

router = APIRouter()

@router.post('/user-register',tags=["User Management"])
async def new_user_registration(deatils : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    return {"Registration" : "Successful"}


@router.post('/organizer-register',
             tags=["Event Management"],
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

    # Check if the file is empty or file doesn't exist
    try : 
        with open(filename, "r") as file:
            existing_data = json.load(file)
    except Exception:
        existing_data = {}                       # Initialise an empty dictionary if the file is empty

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
    
    username = details.user_name
    data = jsonable_encoder(details)

    # Store the response in JSON file
    create_response_json(username,data,filename)
    return JSONResponse(
        content={"message" : "Registration is Successful"},
        status_code=201
    )
