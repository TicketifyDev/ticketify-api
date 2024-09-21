from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from src.schemas.auth_schema import AuthModel
from src.common.json_operations import read_json_data
from src.common.utils import authenticate_user, response_content
from src.auth.auth_token import create_access_token
from pathlib import Path
from datetime import timedelta

async def organizer_login(details : AuthModel):
    """ 
    Function for authenticating organizers and generating access tokens by validating their `username` and `password`.
    """

    # Navigate to the directory where json file with organizer details exists
    parent_directory= Path(__file__).parents[2]
    response_file="organizer_details.json"
    filename = parent_directory / 'responses' / response_file

    # Get all organizers information
    existing_data = read_json_data(filename)

    # Authenticate Organizer details
    organizer = authenticate_user(existing_data, details.username, details.password)
    if not organizer:
        raise HTTPException(
            detail=response_content(
                401,
                "Invalid Credentials",
                errors=[
                    {
                        "field": ["username","password"],
                        "message": "Invalid username or password."
                    }
                ]
            ),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if the account is under review
    if organizer.get("registration_status") == "under_review":
        raise HTTPException(
            detail=response_content(
                401,
                "Your account is still being reviewed. Please wait until one of our Administrators approves it.",
                errors=[
                    {
                        "field": "registration_status",
                        "message": "Account status is under review."
                    }
                ]
            ),
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Check if the account is rejected
    if organizer.get("registration_status") == "rejected":
        raise HTTPException(
            detail=response_content(
                401,
                "Your account has been REJECTED by our Administrators.",
                errors=[
                    {
                        "field": "registration_status",
                        "message": "Account status is Rejected"
                    }
                ]
            ),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT Access Token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data = {
            "sub" : details.username,
            "name" : organizer["name"],
            "role" : "organizer"
        }, 
        expires_delta = access_token_expires
        )
    
    return JSONResponse(
        content=response_content(
            200,
            "Login successful",
            data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": 1800
                }
        ),
        status_code=status.HTTP_200_OK
    )


