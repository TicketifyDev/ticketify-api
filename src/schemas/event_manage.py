from pydantic import BaseModel, EmailStr, Field
from datetime import date, time,datetime
from typing import Optional


class ticket_details(BaseModel):
    price : int = Field( default=150)
    total_tickets : int = Field( default=100)
    available_tickets : int = Field( default=100)

class venue_list(BaseModel):
    name : str
    location : str
    ticket_details : ticket_details

class create_event(BaseModel):
    title : str
    release_date : date
    duration : int = Field( default=180)
    language : str
    genre : list[str]
    cast : Optional[list[str]] = None
    crew : Optional[list[str]] = None
    venues : list[venue_list]