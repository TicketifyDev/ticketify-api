from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.common.constants import USER_LOGIN_COLLECTION
from src.schemas.auth_schema import AuthModel
from src.common.utils import response_content, authenticate_user
from src.auth.auth_token import create_access_token
from datetime import timedelta, timezone, datetime


storeCollection = MongoDB(USER_LOGIN_COLLECTION)
async def user_login(details : AuthModel, collection, request : Request):
    """ 
    Function for authenticating users and generating access tokens by validating their `username` and `password`.
    """
    logger.info(f"Starting user login process for user '{details.username}'.")
    
    # Authenticate User details
    logger.debug(f"Fetching user details for username '{details.username}'")
    user = await collection.read({"user_name": details.username})
    if not user or not authenticate_user(user, details.username, details.password):
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
    logger.debug(f"Generating access token for username '{details.username}'")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data = {
            "sub" : details.username,
            "name" : user["name"],
            "role" : "user"
        }, 
        expires_delta = access_token_expires
        )
    
    # Get current timestamp for last login
    last_login_time = datetime.now(timezone.utc).isoformat()

    # Update last login timestamp in the user's document
    logger.debug(f"Updating last login time for username '{details.username}'")
    await collection.update({"user_name": details.username}, {"last_login_time": last_login_time})

    # Replace with actual client IP and user agent
    ip_address = request.client.host
    user_agent = request.headers.get('user-agent')

    # login details for storage
    login_details = {
        "user_name": details.username,
        "login_time": last_login_time,
        "login_status": "successful",
        "ip_address": ip_address,  
        "user_agent": user_agent   
    }
    
    logger.debug(f"Storing login history of username '{details.username}' into db.")
    await storeCollection.create(login_details)

    logger.debug(f"Login successful for username '{details.username}'.")
    return JSONResponse(
        content=response_content(
            200,
            "Login successful",
            data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "last_login": last_login_time
                }
        ),
        status_code=status.HTTP_200_OK
    )


