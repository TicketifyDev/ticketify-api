from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.logging_config import logger

async def list_of_admins(credentials : HTTPAuthorizationCredentials, collection):
    """
    Admins info retrieval function.
    """

    logger.info("Admins info retrieval attempt initiated.")

    token = credentials.credentials
    username, role = decode_access_token(token)

    logger.debug(f"Decoded token for username '{username}' , role : '{role}'.")

    required_roles = ['admin']
    validate_roles(required_roles, role)

    # Get the details of logged in admin
    logger.debug("Accessing the database to retrieve complete information on all administrators")
    admins = await collection.read_many({})

    admins_list = []
    for admin in admins:
        if admin["user_name"] == username:
            continue    #exclude logged in admin info
        
        del admin["password"]   
        del admin["_id"] 
        
        admins_list.append(admin)                 

    admin = jsonable_encoder(admins_list)

    logger.debug(f"Retrieved {len(admins_list)} admin profiles successfully.")

    return JSONResponse(
        content=response_content(
            200,
            "Successfully retrieved Admin's profile information.",
            admins_list
        ),
        status_code=status.HTTP_200_OK
    )


