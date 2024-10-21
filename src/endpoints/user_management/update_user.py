from pathlib import Path
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from src.common.json_operations import read_json_data, create_json_response
from src.common.utils import response_content, validate_unique_fields
from src.schemas.update_profile_schema import update_user_details
from src.auth.auth_token import decode_access_token, validate_roles
from fastapi.security import HTTPAuthorizationCredentials


async def update_user(
    details: update_user_details,
    credentials: HTTPAuthorizationCredentials,
    collection
):
    ''' Function to update user's profile information. '''

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['user']
    validate_roles(required_roles, role)
    
    #Find the user
    user = await collection.read({"user_name": username})

    # Copy the existing data
    updated_data = user.copy()

    # Loop through the key-value pairs of the payload, excluding unset fields
    for key, value in details.model_dump(exclude_unset=True).items():

        # Check if the value is a dictionary (to handle nested dictionaries)
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():

                # Update with the new values
                updated_data[key][nested_key] = nested_value
        else:
            # Update the non-nested fields with the new values
            updated_data[key] = str(value)

    # Fetch all users information
    user_data = await collection.read_all()
    
    # Iterate through all users information to validate uniqueness
    await validate_unique_fields(user_data, updated_data, username, role)

    # additional fields
    updated_data["updation_date"] = datetime.now(timezone.utc).isoformat()

    # Update the target document if validation passes
    modified_count = await collection.update({"user_name": username}, updated_data)

    if modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response_content(
                404,
                "User details not found or no fields were updated."
            )
        )

    # Exclude fields that are not required
    del updated_data['_id']

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_content(
            200,
            "Successfully updated user information.",
            updated_data
        )
    )