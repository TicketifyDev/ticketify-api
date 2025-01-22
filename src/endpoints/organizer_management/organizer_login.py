from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from src.common.constants import ORGANIZER_LOGIN_COLLECTION
from src.schemas.auth_schema import AuthModel
from src.common.utils import authenticate_user, response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.auth.auth_token import create_access_token
from src.auth.auth_token import create_access_token, create_refresh_token
from datetime import timedelta, datetime, timezone

storeCollection = MongoDB(ORGANIZER_LOGIN_COLLECTION)

async def organizer_login(details : AuthModel, collection : MongoDB, request : Request):
    """ 
    Function for authenticating organizers and generating access tokens by validating their `username` and `password`.
    """
    logger.info(f"Starting organizer login process for organizer '{details.username}'.")

    # Fetch the organizer data from MongoDB by username
    logger.debug(f"Fetching organizer details for username '{details.username}'")
    organizer = await collection.read({"user_name": details.username})

    # If the organizer doesn't exist or the password is incorrect
    if not organizer or not authenticate_user(organizer, details.username, details.password):
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
    
    # Check if the account is under review
    if organizer.get("registration_status") == "under_review":
        raise HTTPException(
            detail=response_content(
                401,
                "Your account is still being reviewed. Please wait until one of our Administrators approves it.",
                errors=[
                    {
                        "field": "registration_status",
                        "message": "Account status is under review."
                    }
                ]
            ),
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Check if the account is rejected
    if organizer.get("registration_status") == "rejected":
        raise HTTPException(
            detail=response_content(
                401,
                "Your account has been REJECTED by our Administrators.",
                errors=[
                    {
                        "field": "registration_status",
                        "message": "Account status is Rejected"
                    }
                ]
            ),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT Access Token
    logger.debug(f"Generating access token for username '{details.username}'")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data = {
            "sub" : details.username,
            "name" : organizer["name"],
            "role" : "organizer"
        }, 
        expires_delta = access_token_expires
        )
    
    # Generate JWT Refresh Token For User
    refresh_token_expires = timedelta(days=7)  # Refresh token valid for 7 days
    refresh_token = create_refresh_token(
        data={
            "sub": details.username,
            "name": organizer["name"],
            "role": "organizer"
        },
        expires_delta=refresh_token_expires
    )
    
    # Get current timestamp for last login
    last_login_time = datetime.now(timezone.utc).isoformat()

    # Update last login timestamp in the organizer's document
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
    
    # Store login details into the login history collection
    logger.debug(f"Storing login history of username '{details.username}' into db.")
    await storeCollection.create(login_details)
    
    logger.debug(f"Login successful for username '{details.username}'.")
    return JSONResponse(
        content=response_content(
            200,
            "Login successful",
            data={
                    "access_token": access_token,
                    "refresh_token": refresh_token,  # Include refresh token in the response
                    "token_type": "bearer",
                    "access_token_expires_in": 1800,  # Access token expiry time (in seconds)
                    "refresh_token_expires_in": 604800, # Refresh token expiry time (in seconds)
                    "last_login": last_login_time
                }
        ),
        status_code=status.HTTP_200_OK
    )