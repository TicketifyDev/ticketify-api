from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pathlib import Path
from common.status_codes import status_codes
from common.json_operations import read_json_data
from common.utils import response_content, authenticate_user
import traceback

router = APIRouter()

@router.get(
    '/check-organizer-status',
    tags=["Organizer Management"],
    status_code=200,
    responses={
        400 : status_codes["response_400"],
        401 : status_codes["response_401"],
        404 : status_codes["response_404"],
        500 : status_codes["response_500"]
    }
)
async def get_organizer_status(username : str = Query(..., min_length=3),
                               password : str = Query(...,min_length=8)):
    """
    API for organizers to check the status of their account registration request.
    """

    try :
        # Navigate to the directory where the JSON file with organizer details exists
        parent_directory= Path(__file__).parents[1]
        response_file="organizer_details.json"
        filename = parent_directory / 'responses' / response_file

        # Read existing organizer data
        organizers_data = read_json_data(filename)

        # Fetch the registration status of the organizer
        if username not in organizers_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response_content(
                    404,
                    f"Organizer account with the username '{username}' does not exist."
                )
            )

        # Authenticate the user by verifying their username and password
        if not authenticate_user(organizers_data, username, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response_content(
                    401,
                    "Invalid Credentials.",
                    errors=[
                        {
                            "field": ["username","password"],
                            "message": "Invalid username or password."
                        }
                    ]
                )
            )

        # Get the registration status of the organizer
        registration_status = organizers_data[username].get('registration_status')
        if not registration_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response_content(
                    404,
                    "Registration status not found."
                )
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content(
                200,
                "Successfully retrieved Registration Status.",
                data={
                        "username": username,
                        "registration_status": registration_status
                    }
            )
        )
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_content(
                500,
                "An unexpected error occurred. Please try again later."
            )
        )
