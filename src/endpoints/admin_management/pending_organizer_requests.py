from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from pathlib import Path
from src.common.json_operations import read_json_data
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content

async def pending_organizer_registration_requests(credentials : HTTPAuthorizationCredentials):
    """
    Function to fetch all registration requests submitted by Organizers that are `under_review`.
    """
    token = credentials.credentials
    _, role = decode_access_token(token)

    required_roles = ['admin']
    validate_roles(required_roles, role)

    #Navigate to the directory where json file with organizer details exists
    parent_directory= Path(__file__).parents[2]
    response_file="organizer_details.json"
    filename = parent_directory / 'responses' / response_file

    organizers_data = read_json_data(filename)

    # Filter organizers whose registration_status is 'under_review'
    under_review_requests = []
    for organizer in organizers_data.values():
        if organizer.get("registration_status") == "under_review":
            # Include only necessary fields for reviewing
            under_review_requests.append({
                    "name": organizer.get('name'),
                    "user_name": organizer.get('user_name'),
                    "email": organizer.get('email'),
                    "phone_number": organizer.get('phone_number'),
                    "organization_details": organizer.get('organization_details'),
                    "registration_status": organizer.get('registration_status'),
                    "registration_date": organizer.get('registration_date')
                })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_content(
            200,
            "Successfully retrieved organizer registration requests that are under review.",
            under_review_requests
        )
    )