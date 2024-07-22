from fastapi import APIRouter, HTTPException, status, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
from pathlib import Path
from common.status_codes import status_codes
from common.json_operations import read_json_data
from auth.auth_token import decode_access_token
from common.utils import response_content, validate_unique_fields
from schemas.update_profile_schema import organizer_profile_update
import traceback, json

router = APIRouter()
token = HTTPBearer()

@router.patch('/organizer-profile',
            tags=["Organizer Management"],
            status_code=200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                404 : status_codes["response_404"],
                409 : status_codes["response_409"],
                500 : status_codes["response_500"]
            })
async def update_organizer_profile(
    details : organizer_profile_update,
    credentials : HTTPAuthorizationCredentials = Security(token)
    ):
    """
    API for organizers to update their profile information.
    """
    try:
        token = credentials.credentials
        username, role = decode_access_token(token)

        # required_roles = ['admin','organizer']
        # validate_roles(required_roles, role)

        #Navigate to the directory where json file with organizer details exists
        current_directory= Path(__file__).parents[1]
        response_file="organizer_details.json"
        filename = current_directory / 'responses' / response_file

        # Read existing organizer data
        organizers_data = read_json_data(filename)

        # Check if the username exists in the data
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
            if isinstance(value, dict):                                             # Check if the value is a dictionary (to handle nested dictionaries)
                for nested_key, nested_value in value.items():
                    updated_data[key][nested_key] = nested_value                    # Update the nested dictionary with the new values
            else:
                updated_data[key] = value                                           # Update the non-nested fields with the new values

        # Validate unique constraints
        unique_fields = ['user_name', 'email', 'phone_number']
        nested_unique_fields = ['organization_name', 'organization_pan_card_number']
        validate_unique_fields(username, updated_data, organizers_data, unique_fields, nested_unique_fields)

        # Add additional fields
        updated_data["updation_date"] = datetime.now(timezone.utc).isoformat()

        # Check if the username has changed
        new_username = updated_data['user_name']
        if new_username != username:
            organizers_data[new_username] = updated_data
            del organizers_data[username]
        else:
            organizers_data[username] = updated_data

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
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_content(
                500,
                "An unexpected error occurred. Please try again later."
            )
        )