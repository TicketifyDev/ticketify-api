from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
from pathlib import Path
from datetime import datetime, timezone
from src.schemas.registration_schema import user_registration
from src.common.json_operations import create_json_response, read_json_data
from src.common.utils import hash_password, response_content
from src.common.constants import CONFLICT_ERROR_CONSTANT

async def user_register(details : user_registration):
    """
    Function to register a new user account
    """

    current_directory= Path(__file__).parents[2]
    response_file_path="user_details.json"
    filename = current_directory / 'responses' / response_file_path
    data = read_json_data(filename)

    for user in data.values():
        #check if user name already exists
        if details.user_name == user["user_name"]:         
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=response_content(
                    409,
                    CONFLICT_ERROR_CONSTANT,
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
        if details.phone_number == user["phone_number"]:         
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=response_content(
                    409,
                    CONFLICT_ERROR_CONSTANT,
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