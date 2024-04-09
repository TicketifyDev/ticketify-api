from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
# import jwt

# Dependency function to verify user credentials
security = HTTPBearer()

# Function to return generated tokens 
def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    return credentials

