from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from common.status_codes import status_codes
from common.json_operations import read_json_data

router = APIRouter()

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
               404 : status_codes["response_404"],
               500 : status_codes["response_500"]
           })
async def get_organizer_profile(username : str):
    """
    API for retrieving organizer's profile information.
    """

    #Navigate to the directory where json file with organizer details exists
    current_directory= Path(__file__).parents[1]
    response_file="organizer_details.json"
    filename = current_directory / 'responses' / response_file

    organizers_data = read_json_data(filename)

    organizer = organizers_data.get(username)
    if organizer is None:
        raise HTTPException(status_code=404, detail=f"Organizer with the user name '{username}' does not exist")
    
    # Exclude the password field
    del organizer["password"]                     

    return JSONResponse(
        content=organizer,
        status_code=200
    )
