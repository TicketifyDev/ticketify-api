from passlib.context import CryptContext
import traceback
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status

VALIDATION_ERROR_CONSTANT = "Validation error occurred"
CONFLICT_ERROR_CONSTANT = "Conflict : The provided value already exists."

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
        if username in data:
            user_dict = data[username]
            hashed_password = user_dict["password"]
            if not verify_password(password, hashed_password):
                return False
            return user_dict
        
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


def check_field_uniqueness(
    current_username: str,
    updated_value: Any,
    organizers_data: Dict[str, Dict[str, Any]],
    field: str,
    is_nested: bool = False
):
    """
    Utility function to check the uniqueness of a single field.

    Parameters :
        `current_username` : The username of the current organizer.
        `updated_value` : The updated value for the field.
        `existing_data` : The existing organizer data.
        `field` : The field to check for uniqueness.
        `is_nested` : Flag to indicate if the field is nested within organization_details.
    """

    if updated_value:
        for existing_username, existing_organizer in organizers_data.items():
            if existing_username != current_username:       # Skip the current user
                if is_nested:
                    if field in existing_organizer.get('organization_details', {}) and \
                       existing_organizer['organization_details'][field] == updated_value:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=response_content(
                                409,
                                CONFLICT_ERROR_CONSTANT,
                                errors=[
                                    {
                                        "field": field,
                                        "message": f"'{updated_value}' is already registered."
                                    }
                                ]
                            )
                        )
                else:
                    if existing_organizer.get(field) == updated_value:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=response_content(
                                409,
                                CONFLICT_ERROR_CONSTANT,
                                errors=[
                                    {
                                        "field": field,
                                        "message": f"'{updated_value}' is already registered."
                                    }
                                ]
                            )
                        )


def validate_unique_fields(
        current_username: str,
        updated_data: Dict[str, Any],
        organizers_data: Dict[str, Dict[str, Any]],
        unique_fields: List[str],
        nested_unique_fields: List[str]
    ):
    """
    Utility function to validate the uniqueness of the values that are passed to the fields.\n
    Checks if any field in the `updated_data` dictionary conflicts with existing data in `organizers_data` dictionary
    for organizer other than the current `username`.

    Parameters :
        `current_username` : The username of the current organizer.
        `updated_data` : The updated data for the organizer.
        `organizers_data` : The existing organizer data.
        `unique_fields` : List of fields that need to be unique across all organizer.
        `nested_unique_fields` : List of nested fields that need to be unique within organization_details.
    """

    for field in unique_fields:
        updated_value = updated_data.get(field)
        check_field_uniqueness(current_username, updated_value, organizers_data, field)

    for field in nested_unique_fields:
        updated_value = updated_data.get('organization_details', {}).get(field)
        check_field_uniqueness(current_username, updated_value, organizers_data, field, is_nested=True)
