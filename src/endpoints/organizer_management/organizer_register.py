from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,timezone
from pathlib import Path
from datetime import datetime, timezone
from src.schemas.registration_schema import organizer_registration
from src.common.json_operations import create_json_response, read_json_data
from src.common.utils import hash_password, response_content, CONFLICT_ERROR_CONSTANT

async def organizer_register(details : organizer_registration):
    """
    Function to register a new organizer account
    """
    parent_directory= Path(__file__).parents[2]
    response_file="organizer_details.json"
    filename = parent_directory / 'responses' / response_file

    existing_data = read_json_data(filename)

    for organizers_data in existing_data.values():
        # Check if username already exists
        if details.user_name == organizers_data["user_name"]:         
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=response_content(
                    409,
                    CONFLICT_ERROR_CONSTANT,
                    errors=[
                        {
                            "field": "user_name",
                            "message": f"The username '{details.user_name}' is already taken."
                        }
                    ]

                )
            )

        # Check if email already exists
        if details.email == organizers_data["email"]:              
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=response_content(
                    409, 
                    CONFLICT_ERROR_CONSTANT,
                    errors=[
                        {
                            "field": "email",
                            "message": f"The email '{details.email}' is already registered."
                        }
                    ]
                )
            )

        # Check if phone number already exists
        if details.phone_number == organizers_data["phone_number"]:              
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=response_content(
                    409, 
                    CONFLICT_ERROR_CONSTANT,
                    errors=[
                        {
                            "field": "phone_number",
                            "message": f"The phone number '{details.phone_number}' is already registered."
                        }
                    ]
                )
            )

        # Check if organization name already exists
        if details.organization_details.organization_name == organizers_data["organization_details"]["organization_name"]: 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=response_content(
                    409, 
                    CONFLICT_ERROR_CONSTANT,
                    errors=[
                        {
                            "field": "organization_name",
                            "message": f"The organization with the name '{details.organization_details.organization_name}' already exists."
                        }
                    ]
                )
            )

        # Check if organization PAN  already exists
        if details.organization_details.organization_pan_card_number == organizers_data["organization_details"]["organization_pan_card_number"]:         
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=response_content(
                    409, 
                    CONFLICT_ERROR_CONSTANT,
                    errors=[
                        {
                            "field": "organization_pan_card_number",
                            "message": f"The PAN card number '{details.organization_details.organization_pan_card_number}' is already associated with another organization. Please verify the details and try again."
                        }
                    ]
                )
            )

    # Hash the password
    hashed_password = hash_password(details.password)

    username = details.user_name
    data = jsonable_encoder(details)

    # Store Hashed password instead of plain password
    data["password"] = hashed_password

    # Add additional fields 
    data["registration_status"] = "under_review"
    data["registration_date"] = datetime.now(timezone.utc).isoformat()

    # Store the response in JSON file
    create_json_response(username,data,filename)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=response_content(
            202,
            "Registration request has been submitted. Your account will be reviewed by our administrator for approval.",
            {
                "user_name" : data["user_name"],
                "email" : data["email"],
                "organization_name" : data["organization_details"]["organization_name"]
            }
        )
    )
