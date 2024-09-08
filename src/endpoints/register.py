from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
from pathlib import Path
from datetime import datetime, timezone
from schemas.registration_schema import user_registration, organizer_registration
from common.json_operations import create_json_response, read_json_data
from common.status_codes import status_codes
from common.utils import hash_password, response_content, CONFLICT_ERROR_CONSTANT, VALIDATION_ERROR_CONSTANT
import traceback

router = APIRouter()

@router.post('/user-register',tags=["User Management"],
             status_code=201,
             responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def new_user_registration(details : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    try:
        current_directory= Path(__file__).parents[1]
        response_file_path="user_details.json"
        filename = current_directory / 'responses' / response_file_path
        data = read_json_data(filename)

        for user in data.values():
            #check if user name already exists
            if details.user_name == user["user_name"]:         
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=response_content(
                        400,
                        VALIDATION_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "user_name",
                                "message": f"The username '{details.user_name}' already exists."
                            }
                        ]

                    )
                )


            # Check if user email already exists
            if details.email == user["email"]:              
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=response_content(
                        400,
                        VALIDATION_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "email",
                                "message": f"The email '{details.email}' is already registered."
                            }
                        ]

                    )
                )

            # Check if phone number already exists
            if details.phone_number == user["phone_number"]:         
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=response_content(
                        400,
                        VALIDATION_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "phone_number",
                                "message": f"The phone number '{details.phone_number}' already exists."
                            }
                        ]

                    )
                )
        #hash the password
        hashed_password = hash_password(details.password)

        username = details.user_name
        data = jsonable_encoder(details)
        data["password"] = hashed_password
        data["registered_date"]=datetime.now(timezone.utc).isoformat()

        # Store the response in JSON file
        create_json_response(username,data,filename)   
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response_content(
                201,
                "User registered successfully",
            )
        )
    #HTTP exception is catched
    except HTTPException as e :
        raise e
    
    #Other exception is Catched
    except Exception as exc :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{exc}' : {exception_details}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_content(
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
    

@router.post('/organizer-register',
             tags=["Organizer Management"],
             status_code=202,
             responses={
                202 : status_codes["response_202"],
                400 : status_codes["response_400"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                }
            )

async def new_organizer_registration(details : organizer_registration):
    """
    API for allowing new organizers to create accounts by providing organizer details.
    """
    try:
        parent_directory= Path(__file__).parents[1]
        response_file="organizer_details.json"
        filename = parent_directory / 'responses' / response_file

        existing_data = read_json_data(filename)

        for organizers_data in existing_data.values():
            # Check if username already exists
            if details.user_name == organizers_data["user_name"]:         
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail=response_content(
                        409,
                        CONFLICT_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "user_name",
                                "message": f"The username '{details.user_name}' is already taken."
                            }
                        ]

                    )
                )

            # Check if email already exists
            if details.email == organizers_data["email"]:              
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail=response_content(
                        409, 
                        CONFLICT_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "email",
                                "message": f"The email '{details.email}' is already registered."
                            }
                        ]
                    )
                )

            # Check if phone number already exists
            if details.phone_number == organizers_data["phone_number"]:              
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail=response_content(
                        409, 
                        CONFLICT_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "phone_number",
                                "message": f"The phone number '{details.phone_number}' is already registered."
                            }
                        ]
                    )
                )

            # Check if organization name already exists
            if details.organization_details.organization_name == organizers_data["organization_details"]["organization_name"]: 
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail=response_content(
                        409, 
                        CONFLICT_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "organization_name",
                                "message": f"The organization with the name '{details.organization_details.organization_name}' already exists."
                            }
                        ]
                    )
                )

            # Check if organization PAN  already exists
            if details.organization_details.organization_pan_card_number == organizers_data["organization_details"]["organization_pan_card_number"]:         
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail=response_content(
                        409, 
                        CONFLICT_ERROR_CONSTANT,
                        errors=[
                            {
                                "field": "organization_pan_card_number",
                                "message": f"The PAN card number '{details.organization_details.organization_pan_card_number}' is already associated with another organization. Please verify the details and try again."
                            }
                        ]
                    )
                )

        # Hash the password
        hashed_password = hash_password(details.password)

        username = details.user_name
        data = jsonable_encoder(details)

        # Store Hashed password instead of plain password
        data["password"] = hashed_password

        # Add additional fields 
        data["registration_status"] = "under_review"
        data["registration_date"] = datetime.now(timezone.utc).isoformat()

        # Store the response in JSON file
        create_json_response(username,data,filename)
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=response_content(
                202,
                "Registration request has been submitted. Your account will be reviewed by our administrator for approval.",
                {
                    "user_name" : data["user_name"],
                    "email" : data["email"],
                    "organization_name" : data["organization_details"]["organization_name"]
                }
            )
        )
    
    # Catches any HTTPException that is raised within the try block and re-raises it
    except HTTPException as http_exc :
        raise http_exc
    
    # Catches all other excepetions
    except Exception as exc :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{exc}' : {exception_details}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_content(
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
