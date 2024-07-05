from passlib.context import CryptContext
from typing import Dict

VALIDATION_ERROR_CONSTANT = "Validation error occurred"

# Initialize CryptContext for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """
    Function to hash a provided plaintext `password` using a secure hashing algorithm.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """
    Function to verify if a provided plaintext `password` matches with the provided hashed value.
    """
    return pwd_context.verify(plain_password, hashed_password)


def response_content(
        status_code : int, 
        message : str, 
        data : Dict={},
        errors : list=[]
    ):
    """
    Utility function to create a standardized API response.

    Args:
        `statusCode` : An integer representing the HTTP status code.
        `message` : A string message providing information about the response.
        `data` : A dictionary containing the response data. Defaults to an empty dictionary if no data is present.
        `errors` : A list of errors encountered during the request processing. Defaults to an empty list if no errors are present.

    """
    return {
        "status_code": status_code,
        "message": message,
        "data": data,
        "errors": errors
    }



