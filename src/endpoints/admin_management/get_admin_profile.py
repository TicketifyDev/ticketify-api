from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.logging_config import logger

async def get_admin_profile(credentials : HTTPAuthorizationCredentials, collection):
    """
    Function for retrieving logged-in admin's profile information.
    """

    logger.info("Admin profile retrieval attempt initiated.")

    token = credentials.credentials
    username, role = decode_access_token(token)

    logger.debug(f"Decoded token for username '{username}' , role : '{role}'.")

    required_roles = ['admin']
    validate_roles(required_roles, role)

    # Get the details of logged in admin
    logger.debug("Fetching admin profile from database for username : '%s'", username)
    admin = await collection.read({"user_name": username})
    
    # Exclude the password field
    del admin["password"]   
    del admin["_id"]                  

    admin = jsonable_encoder(admin)

    logger.debug(f"Organizer profile retrieved successfully for username '{username}'.")

    return JSONResponse(
        content=response_content(
            200,
            "Successfully retrieved Admin's profile information.",
            admin
        ),
        status_code=status.HTTP_200_OK
    )


