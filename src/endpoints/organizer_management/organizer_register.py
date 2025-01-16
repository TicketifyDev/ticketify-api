from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
from src.schemas.registration_schema import organizer_registration
from src.common.utils import hash_password, response_content
from src.common.constants import CONFLICT_ERROR_CONSTANT
from src.common.db import MongoDB
from src.common.logging_config import logger

async def organizer_register(details : organizer_registration, collection : MongoDB):
    """
    Function to register a new organizer account in MongoDB.

    Args:
        details : The registration details of the organizer.
        collection : MongoDB collection to store organizer details.
    """
    logger.info(f"Starting organizer registration process for organizer '{details.user_name}'.")

    # Check if username already exists
    logger.debug(f"Checking if username '{details.user_name}' already exists.")
    existing_user = await collection.read({"user_name": details.user_name})
    if existing_user:
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
    logger.debug(f"Checking if organization name '{details.organization_details.organization_name}' already exists.")
    existing_org = await collection.read({"organization_details.organization_name": details.organization_details.organization_name})
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "organization_name", 
                        "message": f"The organization with the name '{details.organization_details.organization_name}' already exists."
                    }
                ]
            )
        )

    # Check if organization PAN already exists
    logger.debug(f"Checking if PAN card number '{details.organization_details.organization_pan_card_number}' already exists.")
    existing_pan = await collection.read({"organization_details.organization_pan_card_number": details.organization_details.organization_pan_card_number})
    if existing_pan:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "organization_pan_card_number", 
                        "message": f"The PAN card number '{details.organization_details.organization_pan_card_number}' is already associated with another organization."
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
    data["registration_status"] = "under_review"
    data["registration_date"] = datetime.now(timezone.utc).isoformat()

    # Insert the organizer's details into the MongoDB collection
    logger.debug(f"Inserting organizer details of username '{details.user_name}' into db.")
    await collection.create(data)

    # Return a success response
    logger.debug(f"Organizer registration successful for username '{details.user_name}'.")
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=response_content(
            202,
            "Registration request has been submitted. Your account will be reviewed by our administrator for approval.",
            {
                "user_name": data["user_name"],
                "email": data["email"],
                "organization_name": data["organization_details"]["organization_name"]
            }
        )
    )
