from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from src.schemas.auth_schema import AuthModel
from src.common.constants import ADMIN_LOGIN_COLLECTION
from src.common.utils import response_content, authenticate_user
from src.common.db import MongoDB
from src.auth.auth_token import create_access_token, create_refresh_token
from datetime import timedelta, datetime, timezone

storeCollection = MongoDB(ADMIN_LOGIN_COLLECTION)

async def admin_login(details : AuthModel, collection : MongoDB, request : Request):
    """ 
    Function for authenticating admins and generating access tokens by validating their `username` and `password`.
    """

    # Fetch the admin data from MongoDB by username
    admin = await collection.read({"user_name": details.username})

    # If the admin doesn't exist or the password is incorrect
    if not admin or not authenticate_user(admin, details.username, details.password):
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
    

    # Check if the account is inactive
    if admin.get("status") != "active":
        raise HTTPException(
            detail=response_content(
                401,
                "The admin account is inactive.",
                errors=[
                    {
                        "field": "status",
                        "message": "Account status is not active"
                    }
                ]
            ),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT Access Token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data = {
            "sub" : details.username,
            "name" : admin["name"],
            "role" : "admin"
        }, 
        expires_delta = access_token_expires
        )
    
    # Generate JWT Refresh Token For User
    refresh_token_expires = timedelta(days=7)  # Refresh token valid for 7 days
    refresh_token = create_refresh_token(
        data={
            "sub": details.username,
            "name": admin["name"],
            "role": "admin"
        },
        expires_delta=refresh_token_expires
    )
    
    # Get current timestamp for last login
    last_login_time = datetime.now(timezone.utc).isoformat()

    # Update last login timestamp in the admin's document
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
    
    await storeCollection.create(login_details)
    
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