from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.registration import UserRegistration

router = APIRouter()

@router.post('/register',tags=["Register"])
async def new_registration(deatils : UserRegistration):
    return {"Registration" : "Successful"}

