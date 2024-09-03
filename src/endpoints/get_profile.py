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

# @router.get('/user-profile',
#             tags=["User Management"],
#             status_code=200,
#            responses={
#                400 : status_codes["response_400"],
#                404 : status_codes["response_404"],
#                500 : status_codes["response_500"]
#            })
# async def get_user_profile():
#     """
#     API for retrieving user's profile information.
#     """


@router.get('/organizer-profile', 
           tags=["Organizer Management"],
           status_code=200,
           responses={
               400 : status_codes["response_400"],
               401 : status_codes["response_401"],
               403 : status_codes["response_401"],
               404 : status_codes["response_404"],
               500 : status_codes["response_500"]
           })
async def get_organizer_profile(credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    API for retrieving logged in organizer's profile information.
    """
    try :
        token = credentials.credentials
        username, role = decode_access_token(token)

        required_roles = ['admin','organizer']
        validate_roles(required_roles, role)

        #Navigate to the directory where json file with organizer details exists
        parent_directory= Path(__file__).parents[1]
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
        
