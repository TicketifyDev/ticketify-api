from fastapi import APIRouter,HTTPException,status, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
from schemas.event_management_schema import create_event
from common.json_operations import create_json_response, read_json_data
from auth.auth_token import decode_access_token, validate_roles
from common.status_codes import status_codes
from common.utils import response_content
import traceback
from datetime import date, datetime

router=APIRouter(tags=["Event Management"])
token = HTTPBearer()
current_directory= Path(__file__).parents[1]
response_file="event_add.json"
event_response_file = current_directory / 'responses' / response_file

@router.post('/create-event',
             status_code=202,
             responses={
                202 : status_codes["response_202"],
                400 : status_codes["response_400"],
                403 : status_codes["response_403"],
                409 : status_codes["response_409"],
                422 : status_codes["response_422"],
                500 : status_codes["response_500"]
                })
async def add_new_event(request: create_event, credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    API for organizers to create new events (movies).
    """
    try:
        token = credentials.credentials
        username, role = decode_access_token(token)

        required_roles = ['admin','organizer']
        validate_roles(required_roles, role)
        title = request.title
        release_date = request.release_date

        existing_data = read_json_data(event_response_file)
        # Check if the title already exists
        for event_details in existing_data:
            if title in event_details:
                return JSONResponse(
                    content=response_content(
                        409,
                        f"The title {title} already exists."
                    ),
                    status_code=status.HTTP_409_CONFLICT
                )
            
        data = jsonable_encoder(request)
        response = {}
        response=data

        # Check if the release date is less than or equal to todays date
        if release_date <= date.today():
            return JSONResponse(
                content=response_content(
                    400,
                    "The release date must be future date."
                ),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Add extra fields to the response data
        response['event_creation_date_and_time'] = datetime.now().isoformat()
        response['event_creation_request_status'] = "Under Review"
        response['created_by'] = username
        
        # Store the response in the JSON file
        create_json_response(title, response, event_response_file)
        return JSONResponse(
                content=response_content(
                    202,
                    "This event will be reviewed by our administrators for approval.",
                    response
                ),
                status_code=status.HTTP_202_ACCEPTED
            )
    except HTTPException as http_exc :
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
    



@router.get('/check-event-status',
             status_code=200,
             responses={
                200 : status_codes["response_200"],
                401 : status_codes["response_401"],
                403 : status_codes["response_403"],
                404 : status_codes["response_404"],
                500 : status_codes["response_500"]
                })
async def check_event_status(title: str = Query(..., description="Title of the event to check the status"), credentials : HTTPAuthorizationCredentials = Security(token)):
    """
    Check the status of an event based on its title.

    This endpoint allows you to retrieve the current status of an event. The event is identified by its title,
    which must be provided as a query parameter. Access to this endpoint requires valid authorization credentials.
    """
    try:
        token = credentials.credentials
        _, role = decode_access_token(token)

        required_roles = ['admin','organizer']
        validate_roles(required_roles, role)
        existing_data = read_json_data(event_response_file)
        
        # Check if the title exists and get the event details
        if title in existing_data:
            event_status = existing_data[title]["event_creation_request_status"]
            return JSONResponse(
                content={
                    "status_code": 200,
                    "message": f"The status of the event is {event_status}"
                },
                status_code=status.HTTP_200_OK
            )
        else:
            raise HTTPException(
                detail=response_content(
                    404,
                    "Event not found.",
                    errors=[
                        {
                            "field": ["title"],
                            "message": f"Provided event {title} not found"
                        }
                    ]
                ),
                status_code=status.HTTP_404_NOT_FOUND
            )
    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{exc}' : {exception_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_content(
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
