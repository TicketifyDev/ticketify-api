from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional

class venue_dates(BaseModel):
    date: date
    times: list[time]

class Screens(BaseModel):
    screen_name: str = Field(...,examples = ["Screen1"], description = "Name of the screen")
    dates: list[venue_dates]

class venue_list(BaseModel):
    """
    Model representing the data required for venue list for the event
    """
    venue_id: str = Field(..., description = "ID of the venue where event is to take place")
    venue_name : str = Field(...,examples = ["PVR"], description = "Name of the venue where event is to take place")
    screens: list[Screens]

class create_event(BaseModel):
    """
    Model representing the data required for creating a event
    """

    title : str = Field(...,description = "Title of the event")
    release_date : date = Field(...,description = "Release date of the event")
    duration : int = Field( default=180, description = "Duration of the event")
    languages : list[str] = Field(..., examples = [["English"],["Hindi"],["Kannada"]], description = "Languages of the event")
    genre : list[str] = Field(..., examples = [["Thriller"],["Comedy"]], description = "Genre of the event")
    censor: str = Field(..., examples = ["UA13+"], description = "Censorship of the event")
    dimension: list[str] = Field(..., examples = [["3D"],["2D"]], description = "Dimension of the event")
    cast : list[str] = Field(..., description = "Cast involved in the event")
    crew : Optional[list[str]] = Field( None, description = "Crew involved in making of the event")
    description : str = Field(..., description = "Description of the event")
    venues : list[venue_list] = Field(...)


class update_event(BaseModel):
    """
    Model representing the data required for updating an event
    """

    title : Optional[str] = Field(None,description = "Title of the event")
    release_date : Optional[date] = Field(None,description = "Release date of the event")
    duration : Optional[int] = Field( None, description = "Duration of the event")
    languages : list[str] = Field(None, examples = [["English"],["Hindi"],["Kannada"]], description = "Languages of the event")
    genre : Optional[list[str]] = Field(None, examples = [["Thriller"],["Comedy"]], description = "Genre of the event")
    censor: str = Field(None, examples = ["UA13+"], description = "Censorship of the event")
    dimension: list[str] = Field(None, examples = [["3D"],["2D"]], description = "Dimension of the event")
    cast : Optional[list[str]] = Field(None, description = "Cast involved in the event")
    crew : Optional[list[str]] = Field( None, description = "Crew involved in making of the event")
    description : str = Field(None, description = "Description of the event")
    venues : Optional[list[venue_list]] = Field(None)