from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.schemas.registration_schema import user_registration
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.endpoints.user_management.user_register import user_register

router = APIRouter(tags=["User Management"])

@router.post('/user-register',
            status_code=201,
            responses={
                201 : status_codes["response_201"],
                400 : status_codes["response_400"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def new_user_registration(details : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    try:
        response = await user_register(details)
        return response
    
    except HTTPException as e :
        raise e

    except Exception as exc:
        handle_internal_server_error(exc)

