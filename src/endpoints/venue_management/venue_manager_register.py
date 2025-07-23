from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
from src.schemas.venue_manager_schema import VenueManagerRegistration
from src.common.utils import hash_password, response_content
from src.common.constants import CONFLICT_ERROR_CONSTANT
from src.common.db import MongoDB
from src.common.logging_config import logger

async def venue_manager_register(details : VenueManagerRegistration, collection : MongoDB):
    """
    Function to register a new venue manager account in MongoDB.

    Args:
        details : The registration details of the venue manager.
        collection : MongoDB collection to store venue manager details.
    """
    logger.info(f"Starting venue manager registration process for venue manager '{details.user_name}'.")

    # Check if username already exists
    logger.debug(f"Checking if username '{details.user_name}' already exists.")
    existing_user = await collection.read({"username": details.user_name})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "username", 
                        "message": f"The username '{details.user_name}' is already taken."
                    }
                ]
            )
        )

    # Check if email already exists
    logger.debug(f"Checking if email '{details.email}' is already registered.")
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
                        "message": f"The email '{details.email}' is already registered."
                    }
                ]
            )
        )

    # Check if phone number already exists
    logger.debug(f"Checking if phone number '{details.phone_number}' is already registered.")
    existing_phone = await collection.read({"phone_number": details.phone_number})
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "phone_number", 
                        "message": f"The phone number '{details.phone_number}' is already registered."
                    }
                ]
            )
        )

    # Check if organization name already exists
    logger.debug(f"Checking if gstin '{details.company_details.gstin}' is already registered.")
    existing_gstin = await collection.read({"company_details.gstin": details.company_details.gstin})
    if existing_gstin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "gstin", 
                        "message": f"The gstin '{details.company_details.gstin}' is already registered."
                    }
                ]
            )
        )

    # Hash the password
    hashed_password = hash_password(details.password)

    # Convert details to JSON-encodable format 
    data = jsonable_encoder(details)
    # Add additional fields 
    current_time = datetime.now(timezone.utc).isoformat()
    # Store Hashed password instead of plain password
    data["password"] = hashed_password

    # Add additional fields 
    data["registration_date"] = current_time
    data["last_updated_at"] = current_time
    data["is_active"] = True

    # Insert the venue manager's details into the MongoDB collection
    logger.debug(f"Inserting venue manager details of venue manager '{details.user_name}' into db.")
    await collection.create(data)

    # Return a success response
    logger.debug(f"Venue Manager registration successful for username '{details.user_name}'.")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response_content(
            201,
            "Venue Manager registration successful",
            {
                "username": data["user_name"],
                "email": data["email"],
                "company_name": data["company_details"]["company_name"]
            }
        )
    )
