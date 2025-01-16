from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


class ticket_details(BaseModel):
    """
    Model representing the data required for the ticket details for a event
    """

    price : int = Field( default=150, description = "Price per ticket")
    total_tickets : int = Field( default=100, description = "Total tickets for the event")
    available_tickets : int = Field( default=100, description = "number of tickets available for booking")

class venue_list(BaseModel):
    """
    Model representing the data required for venue list for the event
    """

    name : str = Field(...,examples = ["PVR"], description = "Name of the venue where event is to take place")
    location : str = Field(..., description = "Location of the venue where event is to take place")
    ticket_details : ticket_details

class create_event(BaseModel):
    """
    Model representing the data required for creating a event
    """

    title : str = Field(...,description = "Title of the event")
    release_date : date = Field(...,description = "Release date of the event")
    duration : int = Field( default=180, description = "Duration of the event")
    language : str = Field(..., examples = ["English","Hindi","Kannada"], description = "Language of the event")
    genre : list[str] = Field(..., examples = [["Thriller"],["Comedy"]], description = "Genre of the event")
    cast : list[str] = Field(..., description = "Cast involved in the event")
    crew : Optional[list[str]] = Field( None, description = "Crew involved in making of the event")
    venues : list[venue_list] = Field(...)


class update_event(BaseModel):
    """
    Model representing the data required for updating an event
    """

    title : Optional[str] = Field(None,description = "Title of the event")
    release_date : Optional[date] = Field(None,description = "Release date of the event")
    duration : Optional[int] = Field( None, description = "Duration of the event")
    language : Optional[str] = Field(None, examples = ["English","Hindi","Kannada"], description = "Language of the event")
    genre : Optional[list[str]] = Field(None, examples = [["Thriller"],["Comedy"]], description = "Genre of the event")
    cast : Optional[list[str]] = Field(None, description = "Cast involved in the event")
    crew : Optional[list[str]] = Field( None, description = "Crew involved in making of the event")
    venues : Optional[list[venue_list]] = Field(None)