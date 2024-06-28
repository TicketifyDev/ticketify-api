import jwt
import secrets
import traceback
from typing import Optional
from datetime import datetime, timedelta, timezone

JWT_SECRET = secrets.token_hex(32)
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
        to_encode.update({"exp": expire})
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
        user = decoded_token.get("sub")
        return user
    
    except Exception as e:
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")
        return None

