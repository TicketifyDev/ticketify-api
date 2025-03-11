from fastapi import APIRouter, HTTPException, Security, Request, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.auth_schema import AuthModel
from src.common.status_codes import status_codes
from src.common.utils import handle_internal_server_error
from src.endpoints.admin_management.admin_login import admin_login
from src.endpoints.admin_management.get_admin_profile import get_admin_profile
from src.endpoints.admin_management.organizer_requests import organizer_registration_requests
from src.endpoints.admin_management.review_organizer_request import review_organizer_registration_request
from src.endpoints.admin_management.add_admin import add_admin
from src.schemas.admin_management_schema import RegistrationStatus, ReviewRequest, AddNewAdmin
from src.common.constants import ADMINS_COLLECTION
from src.common.constants import ORGANIZERS_COLLECTION
from src.common.db import MongoDB, MongoDBCollectionProvider
from src.common.logging_config import logger

router = APIRouter(prefix="/api/v1/admins", tags=["Admin Management"])
token = HTTPBearer()

# Create an instance of MongoDB class by providing a collection name
collection = MongoDB(ADMINS_COLLECTION)
organizers_collection = MongoDB(ORGANIZERS_COLLECTION)


@router.post('/login',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                500 : status_codes["response_500"]
             })
async def login_as_admin(
    details : AuthModel, 
    request : Request,
    admins_collection : MongoDB = Depends(MongoDBCollectionProvider(ADMINS_COLLECTION))
    ):

    """ 
    API for authenticating admins and generating access tokens by validating their `username` and `password`.
    """
    logger.info("'/admins/login' API is invoked.")
    try :
        logger.debug(f"Login attempt by admin '{details.username}'.")
        response = await admin_login(details, admins_collection, request)
        logger.info("Admin login successful.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in '/admins/login' : {exc}")
        handle_internal_server_error(exc)
        

@router.get('/profile',
            status_code=200,
            responses={
               400 : status_codes["response_400"],
               401 : status_codes["response_401"],
               403 : status_codes["response_401"],
               404 : status_codes["response_404"],
               500 : status_codes["response_500"]
           })
async def fetch_admin_profile(
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(ADMINS_COLLECTION))
):
    """
    API for retrieving logged-in admin's profile information.
    """
    logger.info("GET '/admins/profile' API is invoked.")
    try :
        logger.debug("Validating token for admin profile retrieval.")
        response = await get_admin_profile(credentials, collection)
        logger.info("Admin profile retrieved successfully.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in '/admins/profile' : {exc}")
        handle_internal_server_error(exc)


@router.post('/add',
            status_code=201,
            responses={
               400 : status_codes["response_400"],
               401 : status_codes["response_401"],
               403 : status_codes["response_401"],
               409 : status_codes["response_409"],
               500 : status_codes["response_500"]
            })
async def add_new_admin(
    details : AddNewAdmin,
    credentials : HTTPAuthorizationCredentials = Security(token),
    collection : MongoDB = Depends(MongoDBCollectionProvider(ADMINS_COLLECTION))
):
    """
    API for administrators to add a new admin to the application.\n
    Only existing admins can add another admin.
    """
    logger.info("'/admins/add' API is invoked.")
    try :
        logger.debug("Validating token for adding new admin.")
        response = await add_admin(details, credentials, collection)
        logger.info("New Admin added successfully.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in '/admins/add' : {exc}")
        handle_internal_server_error(exc)


@router.get('/organizer-requests',
            status_code = 200,
            responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            }
        )
async def get_organizer_registration_requests(
    status : RegistrationStatus,
    credentials : HTTPAuthorizationCredentials = Security(token),
    page : int = Query(1, description="Page number"),
    page_size : int = Query(10, description="Number of records per page")
    ):
    """
    API for administrators to view organizer registration requests based on their registration status.\n

    Args:\n
        status : The registration status to filter by
        page : The current page number (default = 1)
        page_size : The number of records per page (default = 10)
    """
    logger.info("GET '/admins/organizer-requests' API is invoked.")
    try:
        logger.debug("Validating token and checking administrator privileges.")
        response = await organizer_registration_requests(credentials, organizers_collection, status, page, page_size)
        logger.info("Successfully fetched organizer registration requests.")
        return response
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        logger.error(f"Unexpected error occurred in '/admins/organizer-requests' : {exc}")
        handle_internal_server_error(exc)

        
@router.patch('/organizers-review/{username}',
              status_code = 200,
              responses={
                400 : status_codes["response_400"],
                401 : status_codes["response_401"],
                403 : status_codes["response_401"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
            })
async def review_organizer_registration(
    username : str,
    review : ReviewRequest,
    credentials : HTTPAuthorizationCredentials = Security(token)
):
    """
    API for administrators to review and approve/reject an organizer's registration request.
    """
    logger.info(f"GET '/admins/organizer-review/{username}' API is invoked.")
    try :
        logger.debug("Validating token and checking administrator privileges.")
        response = await review_organizer_registration_request(
            username,
            review,
            organizers_collection,
            credentials
        )
        logger.info("Successfully reviewed organizer registration requests.")
        return response

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e :
        logger.error(f"Unexpected error occurred in '/admins/organizer-review/{username}' : {e}")
        handle_internal_server_error(e)


@router.get('/event-requests',
            status_code=200,
            responses={

            })
async def get_event_registration_requests():
    # implementation goes here
    pass
