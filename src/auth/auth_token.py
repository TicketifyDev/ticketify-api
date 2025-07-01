import jwt
import os
import traceback
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import status, HTTPException
from dotenv import load_dotenv
from src.common.utils import response_content

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = "HS256"

def create_access_token(data : dict, expires_delta : Optional[timedelta] = None) -> str:
    """
    Function to generate a JSON Web Token (JWT) for user authentication.

    Args:
        data (dict): The user data to encode into the token.
        expires_delta (Optional[timedelta]): An optional timedelta object specifying the token's expiration time. 
                                             If not provided, the token will expire in 15 minutes.

    Returns:
        str: The encoded JWT token(access token).
    """
    try : 
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"iat" :datetime.now(timezone.utc),
                          "exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    except Exception as e :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")



def decode_access_token(token : str):
    """
    Function to decode the JWT access token and extract the user information.
    """
    try: 
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        username = decoded_token.get("sub")
        role = decoded_token.get("role")
        return username, role
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response_content(
                401,
                "Token has expired."
            )
        )

    except (jwt.InvalidSignatureError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response_content(
                401,
                "Invalid access token."
            )
        )

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


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Function to generate a JSON Web Token (JWT) for refreshing user authentication.

    Args:
        data (dict): The user data to encode into the refresh token.
        expires_delta (Optional[timedelta]): An optional timedelta object specifying the refresh token's expiration time.
                                             If not provided, the refresh token will expire in 7 days.

    Returns:
        str: The encoded JWT token (refresh token).
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)  # Default expiration for refresh token is 7 days
        to_encode.update({"iat": datetime.now(timezone.utc),
                          "exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    except Exception as e:
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")



def validate_roles(roles_list : list, role : str):
    """
    Function to check if a user/role has necessary permissions to access a resource. 

    Parameters :
        `roles_list` : A List of roles eligible to access a resource
        `role` : A role that is decoded from access token
    """

    if role not in roles_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=response_content(
                    403,
                    "Access Denied : You do not have access to this resource."
                )
            )