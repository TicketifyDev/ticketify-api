from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from schemas.auth_schema import AuthModel
from common.status_codes import status_codes
from common.json_operations import read_json_data
from common.utils import authenticate_user
from auth.auth_token import create_access_token
from pathlib import Path
from datetime import timedelta
import traceback

router = APIRouter()

@router.post('/organizer-login',
             tags=["Organizer Management"],
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                500 : status_codes["response_500"]
             })
async def login_as_organizer(details : AuthModel):

    """ 
    API for authenticating organizers and generating access tokens by validating their `username` and `password`.
    """

    try :
        # Navigate to the directory where json file with organizer details exists
        current_directory= Path(__file__).parents[1]
        response_file="organizer_details.json"
        filename = current_directory / 'responses' / response_file

        # Get all organizers information
        existing_data = read_json_data(filename)

        # Authenticate Organizer details
        organizer = authenticate_user(existing_data, details.username, details.password)
        if not organizer:
            return JSONResponse(
                content={"message" : "Invalid credentials"},
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
            content = {
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 1800
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

