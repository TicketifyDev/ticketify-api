from passlib.context import CryptContext
from typing import Dict, List, Optional

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
        data : Optional[Dict] = None,
        errors : Optional[List] = None
    ):
    """
    Utility function to create a standardized API response.

    Args:
        `statusCode` : An integer representing the HTTP status code.
        `message` : A string message providing information about the response.
        `data` : A dictionary containing the response data. Defaults to None if data is not provided when calling the function.
        `errors` : A list of errors encountered during the request processing. Defaults to None if errors is not provided when calling the function.

    """

    response = {
        "status_code": status_code,
        "message": message
    }

    if data is not None and data != {}:
        response["data"] = data
    if errors is not None and errors != []:
        response["errors"] = errors

    return response



