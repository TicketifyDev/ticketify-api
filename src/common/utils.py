from passlib.context import CryptContext
import traceback
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status

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


def authenticate_user(data : dict, username: str, password: str):
    """
    Function to Authenticate a user by verifying their `username` and `password`.
    """
    try:
        if data["user_name"] == username:
            hashed_password = data["password"]
            if not verify_password(password, hashed_password):
                return False
            return True
        
    except Exception as e :
        exception_details = traceback.format_exc()
        print(f"An error occurred due to '{e}' : {exception_details}")
        return False
    
    

def handle_internal_server_error(exc: Exception):
    """
    Function to handle internal server errors and format the response.

    Args:
        exc (Exception): The caught exception.

    Returns:
        HTTPException: An HTTPException with a 500 status code and formatted response.
    """
    exception_details = traceback.format_exc()
    print(f"An error occurred due to '{exc}' : {exception_details}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "status_code" : 500,
            "message" : "An unexpected error occurred. Please try again later."
        }
    )

    
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


async def validate_unique_fields(organizers_data : list, updated_data : dict, username : str):
    """
    Utility function to validate the uniqueness of fields like `email`, `phone_number`,
    `organization_name`, and `organization_pan_card_number`.

    Args:
        organizers_data : List of all organizer documents.
        updated_data : The updated data for the organizer being modified.
        username : The username of the organizer being updated.

    Raises:
        HTTPException: If a unique field value already exists in another organizer's data.
    """
    for organizer in organizers_data:
        if organizer["user_name"] != username:  # Skip the current organizer being updated

            # Check if the email already exists
            if updated_data["email"] == organizer["email"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=response_content(
                        409,
                        "Email is already registered.",
                        errors=[{"field": "email", "message": "Email must be unique."}]
                    )
                )

            # Check if the phone number already exists
            if updated_data["phone_number"] == organizer["phone_number"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=response_content(
                        409,
                        "Phone number is already registered.",
                        errors=[{"field": "phone_number", "message": "Phone number must be unique."}]
                    )
                )

            # Check if the organization name already exists
            if updated_data["organization_details"]["organization_name"] == organizer["organization_details"]["organization_name"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=response_content(
                        409,
                        "Organization name is already taken.",
                        errors=[{"field": "organization_name", "message": "Organization name must be unique."}]
                    )
                )

            # Check if the organization PAN card number already exists
            if updated_data["organization_details"]["organization_pan_card_number"] == organizer["organization_details"]["organization_pan_card_number"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=response_content(
                        409,
                        "Organization PAN card number is already taken.",
                        errors=[{"field": "organization_pan_card_number", "message": "PAN card number must be unique."}]
                    )
                )