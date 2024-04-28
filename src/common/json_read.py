import json
from pathlib import Path

current_directory= Path(__file__).parents[1]
response_file="status_codes.json"
filename = current_directory / 'common' / response_file

with open(filename,"r") as file:
    status_codes = json.load(file)
