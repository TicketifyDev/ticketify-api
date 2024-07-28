from fastapi import APIRouter, HTTPException, status, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pathlib import Path
from common.status_codes import status_codes
from common.json_operations import read_json_data
from auth.auth_token import decode_access_token, validate_roles
from common.utils import response_content
import traceback

router = APIRouter()
token = HTTPBearer()

@router.get('/pending-organizer-requests',
            tags=["Admin Management"],
            status_code = 200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            }
        )
async def get_pending_organizer_registration_requests(credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    API for administrators to view all registration requests submitted by Organizers that are `under_review`.
    """
    try:
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
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{exc}' : {exception_details}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_content(
                500,
                "An unexpected error occurred. Please try again later.",
                errors=[
                    {
                        "field": "general", 
                        "message": str(exc)
                    }
                ]
            )
        )