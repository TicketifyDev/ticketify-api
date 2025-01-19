from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.schemas.update_profile_schema import organizer_profile_update
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content, validate_unique_fields
from src.common.db import MongoDB
from datetime import datetime, timezone

async def organizer_profile_get(credentials : HTTPAuthorizationCredentials, collection : MongoDB):
    """
    Function for retrieving logged in organizer's profile information.
    """

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['organizer']
    validate_roles(required_roles, role)

    organizer = await collection.read({"user_name": username})
    
    # Exclude fields that are not required
    del organizer["password"]     
    del organizer["_id"]  

    organizer = jsonable_encoder(organizer)        

    return JSONResponse(
        content=response_content(
            200,
            "Successfully retrieved profile information.",
            organizer
        ),
        status_code=status.HTTP_200_OK
    )


async def update_organizer(
    details : organizer_profile_update,
    credentials : HTTPAuthorizationCredentials,
    collection : MongoDB
    ):
    """
    Function to update organizers profile information.
    """

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['organizer']
    validate_roles(required_roles, role)

    organizer = await collection.read({"user_name": username})

    # Copy the existing data
    updated_data = organizer.copy()

    # Loop through the key-value pairs of the payload, excluding unset fields
    for key, value in details.model_dump(exclude_unset=True).items():  

        # Check if the value is a dictionary (to handle nested dictionaries)         
        if isinstance(value, dict):                                             
            for nested_key, nested_value in value.items():
                
                # Update the nested dictionary with the new values
                updated_data[key][nested_key] = nested_value                    
        else:
            # Update the non-nested fields with the new values
            updated_data[key] = value                                           

    # Fetch all organizers' documents
    organizers_data = await collection.read_all()

    # Iterate through all organizers to validate uniqueness
    await validate_unique_fields(organizers_data, updated_data, username, role)

    # Add additional fields
    updated_data["updation_date"] = datetime.now(timezone.utc).isoformat()

    # Update the target document if validation passes
    modified_count = await collection.update({"user_name": username}, updated_data)

    if modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response_content(
                404,
                "Organizer not found or no fields were updated."
            )
        )

    # Exclude fields that are not required
    del updated_data['password']
    del updated_data['_id']

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_content(
            200,
            "Successfully updated profile information.",
            updated_data
        )
    )