from fastapi import HTTPException
import json
import traceback

def create_response_json(unique_id, data_dict, file_location):
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
