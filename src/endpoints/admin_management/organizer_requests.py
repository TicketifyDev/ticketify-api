from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.auth_token import decode_access_token, validate_roles
from src.common.utils import response_content
from src.common.db import MongoDB
from src.common.logging_config import logger
import math

async def organizer_registration_requests(
        credentials : HTTPAuthorizationCredentials, 
        collection : MongoDB, 
        status : str,
        page : int, 
        page_size : int
    ):
    """
    Function to fetch paginated registration requests based on status submitted by Organizers.
    """

    logger.info("Fetching organizer registration requests with status: %s, page: %d, page_size: %d", status, page, page_size)

    token = credentials.credentials
    username, role = decode_access_token(token)

    logger.debug(f"Decoded token for username '{username}' , role : '{role}'.")

    required_roles = ['admin']
    validate_roles(required_roles, role)

    # Define the query filter based on the 'status'
    query = {}
    if status:
        query["registration_status"] = status
        logger.debug("Query filter applied: %s", query)

    # Fetch the total number of organizers based on the filter
    total_organizers_count = await collection.count_documents(query)
    logger.debug("Total organizers count matching the query: %d", total_organizers_count)

    # Calculate total pages
    total_pages = math.ceil(total_organizers_count / page_size)
    logger.debug("Total pages calculated: %d", total_pages)

    # Prevent page overflow
    if page > total_pages and total_organizers_count > 0:
        raise HTTPException(
            status_code=400,
            detail=response_content(
                400, 
                f"Page {page} does not exist. The maximum page is {total_pages}."
            )
        )

    # Fetch organizers based on status, skip/limit for pagination
    skip = (page - 1) * page_size
    organizers_data = await collection.read_many(query, skip=skip, limit=page_size)

    # Only include necessary fields for reviewing
    registration_requests = []
    for organizer in organizers_data:
        registration_requests.append({
                "name": organizer.get('name'),
                "user_name": organizer.get('user_name'),
                "email": organizer.get('email'),
                "phone_number": organizer.get('phone_number'),
                "organization_details": organizer.get('organization_details'),
                "registration_status": organizer.get('registration_status'),
                "registration_date": organizer.get('registration_date')
            })
        
    # Convert the enum status value to a user-friendly message format
    status_message = status.value.replace("_", " ").title()  

    logger.debug("Successfully fetched organizer registration requests with status: %s", status)

    # Return paginated response
    return JSONResponse(
        status_code=200,
        content=response_content(
            200,
            f"Successfully retrieved organizer registration requests that are '{status_message}'." if status else 
            "Successfully retrieved all organizer registration requests.",
            {
                "requests": registration_requests,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_organizers_count": total_organizers_count
            }
        )
    )