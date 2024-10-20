from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.db import MongoDB

async def pending_organizer_registration_requests(credentials : HTTPAuthorizationCredentials, collection : MongoDB):
    """
    Function to fetch all registration requests submitted by Organizers that are `under_review`.
    """
    token = credentials.credentials
    _, role = decode_access_token(token)

    required_roles = ['admin']
    validate_roles(required_roles, role)

    organizers_data = await collection.read_all()

    # Filter organizers whose registration_status is 'under_review'
    under_review_requests = []
    for organizer in organizers_data:
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
            "Successfully retrieved organizer registration requests that are 'under review'.",
            under_review_requests
        )
    )