from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content

async def get_admin_profile(credentials : HTTPAuthorizationCredentials, collection):
    """
    Function for retrieving logged-in admin's profile information.
    """

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['admin']
    validate_roles(required_roles, role)

    # Get the details of logged in admin
    admin = await collection.read({"user_name": username})
    
    # Exclude the password field
    del admin["password"]   
    del admin["_id"]                  

    admin = jsonable_encoder(admin)

    return JSONResponse(
        content=response_content(
            200,
            "Successfully retrieved Admin's profile information.",
            admin
        ),
        status_code=status.HTTP_200_OK
    )


