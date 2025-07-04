from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.constants import CONFLICT_ERROR_CONSTANT
from src.common.utils import response_content, hash_password
from src.common.db import MongoDB
from src.common.logging_config import logger
from src.schemas.admin_management_schema import AddNewAdmin
from datetime import datetime, timezone


async def add_admin(details : AddNewAdmin, credentials : HTTPAuthorizationCredentials, collection : MongoDB):
    """ 
    Function for authenticating admins and allowing them to add more admins to the application.
    """

    logger.info(f"Initiating process to add a new admin: '{details.user_name}'.")
    
    token = credentials.credentials
    username, role = decode_access_token(token)

    logger.debug(f"Decoded token for username '{username}' , role : '{role}'.")

    required_roles = ['admin']
    validate_roles(required_roles, role)

    # Check if the username already exists
    existing_username = await collection.read({"user_name": details.user_name})
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "user_name", 
                        "message": f"The username '{details.user_name}' is already taken."
                    }
                ]
            )
        )
    

    # Check if the email already exists
    existing_email = await collection.read({"email": details.email})
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "email", 
                        "message": f"The email '{details.email}' is already taken."
                    }
                ]
            )
        )
    
    # Hash the password
    hashed_password = hash_password(details.password)

    # Convert details to JSON-encodable format 
    data = jsonable_encoder(details)

    # Store Hashed password instead of plain password
    data["password"] = hashed_password

    # Add additional fields 
    current_time = datetime.now(timezone.utc).isoformat()
    data["creation_date"] = current_time
    data["status"] = "new_user"
    data["initial_admin"] = False
    data["created_by"] = username
    data["last_updated_by"] = username
    data["last_updated_at"] = current_time

    # Insert new admin details into the MongoDB collection
    logger.debug(f"Saving new admin '{details.user_name}' to the database.")
    await collection.create(data)

    # Return a success response
    logger.debug(f"New Admin '{details.user_name}' added successfully by '{username}'.")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response_content(
            201,
            "Admin added successfully.",
            {
                "name": data["name"],
                "user_name": data["user_name"],
                "email": data["email"]
            }
        )
    )