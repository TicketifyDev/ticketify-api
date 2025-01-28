from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.common.logging_config import logger
from fastapi.security import HTTPAuthorizationCredentials
from src.common.json_operations import read_json_data
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from pathlib import Path

async def get_user_profile(credentials : HTTPAuthorizationCredentials, collection):
    """
    Function for retrieving logged-in user's profile information.
    """

    logger.info("Fetching user profile information.")
    token = credentials.credentials
    username, role = decode_access_token(token)
    logger.debug(f"Decoded token for username '{username}' , role : '{role}'.")

    required_roles = ['user']
    validate_roles(required_roles, role)

    # Get the details of logged in user
    logger.debug(f"Fetching the details of logged in user {username}")
    user = await collection.read({"user_name": username})
    
    # Exclude the password field
    del user["password"]   
    del user["_id"]                  

    user = jsonable_encoder(user)

    logger.debug(f"User profile retrieved successfully for username '{username}'.")
    return JSONResponse(
        content=response_content(
            200,
            "Successfully retrieved User's profile information.",
            user
        ),
        status_code=status.HTTP_200_OK
    )


