from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Zone(BaseModel):
    zone_name: str
    price: float
    rows: List[str]

class Pricing(BaseModel):
    zones: List[Zone]

class SeatingLayout(BaseModel):
    rows: int
    columns: int

class Screen(BaseModel):
    screen_name: str
    seating_layout: SeatingLayout
    pricing: Pricing
    features: Optional[List[str]] = []

class Location(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str

class VenueBase(BaseModel, extra = 'forbid'):
    name: str
    location: Location
    screens: List[Screen]
    features: Optional[List[str]] = []


class VenueUpdateRequest(BaseModel, extra = 'forbid'):
    name: Optional[str] = None
    location: Optional[Location] = None
    screens: Optional[List[Screen]] = None
    features: Optional[List[str]] = None

