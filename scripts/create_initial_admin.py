import sys
import getpass 
import re
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Determine the parent directory of the current script's file path.
parent_directory_resolved = Path(__file__).resolve().parents[1]

# Add the parent directory to the sys.path list to allow importing modules from that directory.
sys.path.append(str(parent_directory_resolved))

from src.common.utils import hash_password
from src.schemas.registration_schema import NAME_REGEX, USERNAME_REGEX, PASSWORD_REGEX, EMAIL_REGEX
from src.common.db import MongoDB
from src.common.constants import ADMINS_COLLECTION
from src.common.logging_config import logger

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


def get_valid_input(prompt: str, regex: str, error_message: str):
    """
    Function to Prompt the user for input and validate it against a regex pattern. \n
    Repeats the prompt until the input is valid.

    Parameters:
        `prompt` : The input prompt message
        `regex` : The regex pattern to validate the input
        `error_message` : The error message to display for invalid input
    """

    while True:
        user_input = input(prompt)
        if re.match(regex, user_input):
            return user_input
        else:
            print(error_message)


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

    name = get_valid_input(
        "\n Enter admin full name : ",
        NAME_REGEX,
        "Invalid name. Name can only contain letters, spaces, apostrophes, and hyphens."
    )

    user_name = get_valid_input(
        "\n Enter admin username : ",
        USERNAME_REGEX,
        "Invalid username. Username must consist of alphanumeric characters and underscores of 3-20 characters."
    )

    email = get_valid_input(
        "\n Enter admin email : ",
        EMAIL_REGEX,
        "Invalid email. Please enter a valid email address."
    )

    while True:
        password = getpass.getpass("\n Enter admin password : ")          # For secure password input
        if re.match(PASSWORD_REGEX,password) :
            break
        else:
            print("Invalid password. Password must be at least 8-32 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character")

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
