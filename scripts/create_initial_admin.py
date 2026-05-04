import sys
import os
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Determine the parent directory of the current script's file path.
parent_directory_resolved = Path(__file__).resolve().parents[1]

# Add the parent directory to the sys.path list to allow importing modules from that directory.
sys.path.append(str(parent_directory_resolved))

from src.common.utils import hash_password
from src.common.db import MongoDB
from src.common.constants import ADMINS_COLLECTION
from src.common.logging_config import logger

name = os.getenv("INITIAL_ADMIN_NAME")
user_name = os.getenv("INITIAL_ADMIN_USERNAME")
email = os.getenv("INITIAL_ADMIN_EMAIL")
password = os.getenv("INITIAL_ADMIN_PASSWORD")

collection = MongoDB(ADMINS_COLLECTION)

async def  check_initial_admin():
    """
    Function to check if the initial Admin account exists and proceed with account creation if it does not.\n
    This function is intended to be used during the startup event in `main.py`. 
    """

    is_empty = await collection.is_collection_empty()
    if is_empty:
        print("\n !! Initial Admin account does not exist. !! \n")
        logger.info("Initial Admin account does not exist.")
        await create_initial_admin()
    else :
        logger.info("Initial Admin account already exists.")


async def create_initial_admin():
    """
    Function to create the first/initial Admin for the application.
    """
    logger.debug("Invoked create_initial_admin() function.")
    is_empty = await collection.is_collection_empty()
    if not is_empty:
        print("\n !! Initial Admin account already exists. !!")
        return 
    
    # Continue to create new admin by prompting user to input admin details if file doesn't exist or is empty
    print("\nCreating Initial Admin account...")
    logger.info("Creating Initial Admin account.")

    time.sleep(1)

    # Hash the password before storing
    hashed_password = hash_password(password)

    # Create admin data dictionary
    admin_data = {
        "name":name,
        "user_name": user_name,
        "email": email,
        "password": hashed_password,
        "creation_date" : datetime.now(timezone.utc).isoformat(),
        "status" : "new_user",
        "initial_admin" : True
    }

    # Store admin data to DB
    await collection.create(admin_data)
    logger.debug("Inserted initial admin data into db")

    print("\n !! Initial Admin account created successfully. !! \n")
    logger.info("Initial Admin account created successfully.")


# This block ensures that the create_initial_admin() function is called only when this script is run directly through command line.
# If this script is imported as a module in another script, the function will not be executed automatically.
if __name__ == "__main__":
    logger.debug("'create_initial_admin.py' module is being executed from the command line.")
    asyncio.run(create_initial_admin())
