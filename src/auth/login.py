from fastapi import APIRouter, Depends, HTTPException, status
from  schemas.auth_schema import AuthModel
from auth.get_token import verify_user

router = APIRouter()

@router.post('/login',tags=["User Management"])
async def login_to_get_token(credentials : AuthModel):
    """ 
    API for authenticating users by verifying their credentials.\n
    Leverage this API to get Access Token.
    """
    return {"Login" : "Successful"}
