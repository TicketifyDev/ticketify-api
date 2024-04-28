import json

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
        print(f"An error occurred while writing to {file_location}: {e}")
