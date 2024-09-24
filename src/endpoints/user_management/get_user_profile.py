from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.common.json_operations import read_json_data
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from pathlib import Path

async def get_user_profile(credentials : HTTPAuthorizationCredentials):
    """
    Function for retrieving logged-in user's profile information.
    """

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['user','admin']
    validate_roles(required_roles, role)

    #Navigate to the directory where json file with user details exists
    parent_directory= Path(__file__).parents[2]
    response_file="user_details.json"
    filename = parent_directory / 'responses' / response_file

    user_data = read_json_data(filename)

    # Get the details of logged in user
    user = user_data.get(username)
    
    # Exclude the password field
    del user["password"]                     

    return JSONResponse(
        content=response_content(
            200,
            "Successfully retrieved User's profile information.",
            user
        ),
        status_code=status.HTTP_200_OK
    )


