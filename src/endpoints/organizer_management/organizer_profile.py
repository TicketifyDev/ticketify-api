from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.schemas.update_profile_schema import organizer_profile_update
from src.common.json_operations import read_json_data
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content, validate_unique_fields
from pathlib import Path
from datetime import datetime, timezone
import json

async def organizer_profile_get(credentials : HTTPAuthorizationCredentials):
    """
    Function for retrieving logged in organizer's profile information.
    """

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['admin','organizer']
    validate_roles(required_roles, role)

    #Navigate to the directory where json file with organizer details exists
    parent_directory= Path(__file__).parents[2]
    response_file="organizer_details.json"
    filename = parent_directory / 'responses' / response_file

    organizers_data = read_json_data(filename)

    # Get the details of logged in organizer
    organizer = organizers_data.get(username)
    
    # Exclude the password field
    del organizer["password"]                     

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
    credentials : HTTPAuthorizationCredentials
    ):
    """
    Function to update organizers profile information.
    """

    token = credentials.credentials
    username, role = decode_access_token(token)

    required_roles = ['admin','organizer']
    validate_roles(required_roles, role)

    #Navigate to the directory where json file with organizer details exists
    current_directory= Path(__file__).parents[2]
    response_file="organizer_details.json"
    filename = current_directory / 'responses' / response_file

    # Read existing organizer data
    organizers_data = read_json_data(filename)

    # Check if the username has changed since last login
    organizer = organizers_data.get(username)
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response_content(
                401,
                "Your 'username' has been updated since last login. Please re-login with the updated credentials."
            )
        )

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

    # Validate unique constraints
    unique_fields = ['email', 'phone_number']
    nested_unique_fields = ['organization_name', 'organization_pan_card_number']
    validate_unique_fields(username, updated_data, organizers_data, unique_fields, nested_unique_fields)

    # Add additional fields
    updated_data["updation_date"] = datetime.now(timezone.utc).isoformat()

    # Check if the username has changed                 # TODO Enable this block of code if needed in future
    # new_username = updated_data['user_name']
    # if new_username != username:
    #     organizers_data[new_username] = updated_data
    #     del organizers_data[username]
    # else:
    #     organizers_data[username] = updated_data

    # Save the updated data back to the JSON file
    with open(filename,"w") as file:
        json.dump(organizers_data, file, indent=4)

    # Exclude the password field
    del updated_data['password']

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_content(
            200,
            "Successfully updated profile information.",
            updated_data
        )
    )