from fastapi import APIRouter, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.auth_schema import AuthModel
from src.schemas.registration_schema import organizer_registration
from src.schemas.update_profile_schema import organizer_profile_update
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.common.db import MongoDB
from src.endpoints.organizer_management.organizer_register import organizer_register
from src.endpoints.organizer_management.organizer_login import organizer_login
from src.endpoints.organizer_management.organizer_status import organizer_status
from src.endpoints.organizer_management.organizer_profile import organizer_profile_get, update_organizer

router = APIRouter(tags=["Organizer Management"])
token = HTTPBearer()

# Create an instance of MongoDB class by providing a collection name
collection = MongoDB("organizers")

@router.post('/organizer-register',
            status_code=202,
            responses={
                202 : status_codes["response_202"],
                400 : status_codes["response_400"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def new_organizer_registration(details : organizer_registration):
    """
    API for allowing new organizers to create accounts by providing organizer details.
    """
    try :
        response = await organizer_register(details, collection)
        return response
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as exc:
        handle_internal_server_error(exc)
    

@router.post('/organizer-login',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                500 : status_codes["response_500"]
             })
async def login_as_organizer(details : AuthModel):

    """ 
    API for authenticating organizers and generating access tokens by validating their `username` and `password`.
    """
    try :
        response = await organizer_login(details, collection)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)


@router.get('/check-organizer-status',
            status_code=200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            })
async def get_organizer_status(username : str = Query(..., min_length=3),
                               password : str = Query(...,min_length=8)):
    """
    API for organizers to check the status of their account registration request.
    """
    try :
        response = await organizer_status(username, password, collection)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)


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
        response = await organizer_profile_get(credentials, collection)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)


@router.patch('/organizer-profile',
            tags=["Organizer Management"],
            status_code=200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
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
    try :
        response = await update_organizer(details, credentials, collection)
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        handle_internal_server_error(exc)