from fastapi import APIRouter
from schemas.registration_schema import user_registration

router = APIRouter()

@router.post('/register',tags=["User Management"])
async def new_user_registration(deatils : user_registration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    return {"Registration" : "Successful"}

