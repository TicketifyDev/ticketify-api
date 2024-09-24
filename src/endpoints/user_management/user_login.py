from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from src.schemas.auth_schema import AuthModel
from src.common.utils import response_content
from src.auth.auth_token import create_access_token
from datetime import timedelta

async def user_login(details : AuthModel, collection):
    """ 
    Function for authenticating users and generating access tokens by validating their `username` and `password`.
    """

    # Authenticate User details
    user = await collection.read({"user_name": details.username})
    if not user:
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
    
    # Generate JWT Access Token For User
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data = {
            "sub" : details.username,
            "name" : user["name"],
            "role" : "user"
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


