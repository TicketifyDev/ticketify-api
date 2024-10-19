from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from src.schemas.auth_schema import AuthModel
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.common.constants import ADMINS_COLLECTION
from src.common.db import MongoDB
from src.endpoints.admin_management.admin_login import admin_login

router = APIRouter(prefix="/api/v1", tags=["Admin Management"])
token = HTTPBearer()

# Create an instance of MongoDB class by providing a collection name
collection = MongoDB(ADMINS_COLLECTION)
    

@router.post('/admin-login',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                500 : status_codes["response_500"]
             })
async def login_as_admin(details : AuthModel):

    """ 
    API for authenticating admins and generating access tokens by validating their `username` and `password`.
    """
    try :
        response = await admin_login(details, collection)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)