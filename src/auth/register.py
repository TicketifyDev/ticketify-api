from fastapi import APIRouter
from schemas.registration_schema import UserRegistration

router = APIRouter()

@router.post('/register',tags=["Register"])
async def new_registration(deatils : UserRegistration):
    """
    API for allowing new users to create accounts by providing user details.
    """
    return {"Registration" : "Successful"}

