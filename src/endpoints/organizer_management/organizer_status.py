from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from src.common.utils import response_content, authenticate_user
from src.common.db import MongoDB

async def organizer_status(
        username : str,
        password : str,
        collection : MongoDB
    ):
    """
    Function to check the status of organizers account registration request.
    """

    # Fetch the organizer data from MongoDB by username
    organizer = await collection.read({"user_name": username})

    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response_content(
                404,
                f"Organizer account with the username '{username}' does not exist."
            )
        )

    # Authenticate the user by verifying their username and password
    if not authenticate_user(organizer, username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response_content(
                401,
                "Invalid Credentials.",
                errors=[
                    {
                        "field": ["username","password"],
                        "message": "Invalid username or password."
                    }
                ]
            )
        )

    # Get the registration status of the organizer
    registration_status = organizer.get('registration_status')
    if not registration_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response_content(
                404,
                "Registration status not found."
            )
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_content(
            200,
            "Successfully retrieved Registration status.",
            data={
                    "username": username,
                    "registration_status": registration_status
                }
        )
    )