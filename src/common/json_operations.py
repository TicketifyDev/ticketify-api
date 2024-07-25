from fastapi import HTTPException
import json
import traceback

def create_json_response(unique_id, data_dict, file_location):
    """
    Method to write responses to json file
    """
    try:
        with open(file_location, 'r') as file:
            existing_data = json.load(file)
    except Exception:
        existing_data = {}
    existing_data[unique_id] = data_dict
    try:
        with open(file_location, 'w') as file:
            json.dump(existing_data, file, indent=4)
    except Exception as e:
        exception_details = traceback.format_exc()
        print(f"An error occurred while writing to {file_location} due to '{e}' : {exception_details}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


def read_json_data(filename):
    """
    Method to read/retrieve the content of json file
    """
    
    # Check if the file is empty or file doesn't exist
    try : 
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except Exception as e:
        exception_details = traceback.format_exc()
        print(f"An error occurred while reading '{filename}' file due to '{e}' : {exception_details}")
        return {}                       # Initialise an empty dictionary if the file is empty
    
