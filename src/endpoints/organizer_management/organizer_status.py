from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pathlib import Path
from src.common.status_codes import status_codes
from src.common.json_operations import read_json_data
from src.common.utils import response_content, authenticate_user
import traceback

async def organizer_status(
        username : str,
        password : str
    ):
    """
    Function to check the status of organizers account registration request.
    """

    # Navigate to the directory where the JSON file with organizer details exists
    parent_directory= Path(__file__).parents[2]
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