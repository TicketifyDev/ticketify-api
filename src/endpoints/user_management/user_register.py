from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
from datetime import datetime, timezone
from src.schemas.registration_schema import user_registration
from src.common.utils import hash_password, response_content
from src.common.constants import CONFLICT_ERROR_CONSTANT

async def user_register(details : user_registration, collection):
    """
    Function to register a new user account
    """

    #check if user name already exists
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
                        "message": f"The username '{details.user_name}' already exists."
                    }
                ]

            )
            )


    # Check if user email already exists
    existing_mail = await collection.read({"email":details.email})
    if existing_mail:              
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
    existing_phone = await collection.read({"phone_number":details.phone_number})
    if existing_phone:         
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=response_content(
                409,
                CONFLICT_ERROR_CONSTANT,
                errors=[
                    {
                        "field": "phone_number",
                        "message": f"The phone number '{details.phone_number}' already exists."
                    }
                ]

            )
        )
    #hash the password
    hashed_password = hash_password(details.password)

    username = details.user_name
    data = jsonable_encoder(details)
    data["password"] = hashed_password
    data["registered_date"]=datetime.now(timezone.utc).isoformat()

    #Storing data in db
    await collection.create(data)  

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response_content(
            201,
            "User registered successfully",
        )
    )