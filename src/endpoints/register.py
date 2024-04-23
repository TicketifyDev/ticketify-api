from fastapi import APIRouter
from schemas.registration_schema import user_registration,organizer_registration

router = APIRouter()

@router.post('/user-register',tags=["User Management"])
async def new_user_registration(deatils : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    return {"Registration" : "Successful"}


@router.post('/organizer-register',tags=["Event Management"])
async def new_organizer_registration(details : organizer_registration):
    """
    API for allowing new organizers to create accounts by providing organizer details.
    """
    return {"Registration" : "Successful"}
