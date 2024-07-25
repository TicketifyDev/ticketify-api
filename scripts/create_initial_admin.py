import sys
import getpass 
import re
import time
from pathlib import Path

# Determine the parent directory of the current script's file path.
parent_directory_resolved = Path(__file__).resolve().parents[1]

# Add the parent directory to the sys.path list to allow importing modules from that directory.
sys.path.append(str(parent_directory_resolved))

from src.common.json_operations import read_json_data, create_json_response
from src.common.utils import hash_password
from src.schemas.registration_schema import NAME_REGEX, USERNAME_REGEX, PASSWORD_REGEX, EMAIL_REGEX

parent_directory = Path(__file__).parents[1]
admin_file = "initial_admin.json"
filename = parent_directory / 'src' / 'responses' / admin_file

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


def create_initial_admin():
    """
    Function to create the first/initial Admin for the application.
    """

    # Check if admin file already exists and has data in it
    admin_data = read_json_data(filename)
    if admin_data:
        print("\n !! Initial Admin account already exists. !!")
        return 
    
    # Continue to create new admin by prompting user to input admin details if file doesn't exist or is empty
    print("\nCreating Initial Admin account...")
    time.sleep(1)
    name = get_valid_input(
        "\n Enter admin full name : ",
        NAME_REGEX,
        "Invalid name. Name can only contain letters, spaces, apostrophes, and hyphens."
    )

    username = get_valid_input(
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
        "username": username,
        "email": email,
        "password": hashed_password
    }

    # Write admin data to JSON file
    create_json_response(username,admin_data,filename)

    print("\n !! Initial Admin account created successfully. !!")


# This block ensures that the create_initial_admin() function is called only when this script is run directly through command line.
# If this script is imported as a module in another script, the function will not be executed automatically.
if __name__ == "__main__":
    create_initial_admin()
