import re
from typing import List
from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator

#Constants for Regex Patterns
NAME_REGEX = r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$"
USERNAME_REGEX = r"^[a-zA-Z0-9_.]+$"
EMAIL_REGEX = r"^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,3})+$"
PHONE_NUMBER_REGEX = r"^[6-9]\d{9}$"
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$"
GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
SEAT_REGEX = r"^[A-Z]\d{1,3}$"  # Like A1, B12, etc.
OBJECT_ID_REGEX = r"^[a-f\d]{24}$"  # MongoDB ObjectId (24 hex chars)


class CompanyAddress(BaseModel, extra='forbid'):
    line1: str = Field(
        min_length=5,
        examples=["Address line 1"],
        description="First line of the venue manager's company address"
    )
    line2: str = Field(
        min_length=5,
        examples=["Address line 2"],
        description="Second line of the venue manager's company address"
    )
    city: str = Field(
        min_length=2,
        examples=["Bangalore"],
        description="City where the venue manager is located"
    )
    state: str = Field(
        min_length=2,
        examples=["Karnataka"],
        description="State where the venue manager is located"
    )
    pincode: str = Field(
        min_length=6,
        max_length=6,
        examples=["XXXXXX"],
        description="Pincode of the venue manager's address"
    )


class VenueManagerCompanyDetails(BaseModel, extra='forbid'):
    company_name: str = Field(
        min_length=3,
        examples=["INOX"],
        description="Name of the venue manager's company"
    )
    gstin: str = Field(
        min_length=15,
        max_length=15,
        examples=["12ABCDE1234F5Z6"],
        description="GSTIN number of the venue manager's company"
    )
    address: CompanyAddress

    @field_validator("company_name")
    def validate_company_name(cls, value):
        if not re.match(NAME_REGEX, value):
            raise ValueError("Invalid company name format")
        return value

    @field_validator("gstin")
    def validate_gstin(cls, value):
        if not re.match(GSTIN_REGEX, value):
            raise ValueError("Invalid GSTIN format")
        return value


class VenueManagerRegistration(BaseModel, extra='forbid'):
    full_name: str = Field(
        min_length=3,
        examples=["John Sharma"],
        description="Full name of the venue manager"
    )
    user_name: str = Field(
        min_length=3,
        examples=["johnsharma12"],
        description="Unique user_name for the venue manager"
    )
    email: EmailStr = Field(
        min_length=10,
        examples=["john@example.com"],
        description="Email address of the venue manager"
    )
    phone_number: str = Field(
        min_length=10,
        max_length=16,
        examples=["string"],
        description="Phone number of the venue manager (may include country code)"
    )
    password: str = Field(
        min_length=8,
        max_length=32,
        examples=["string"],
        description="Password for the venue manager's account"
    )
    company_details: VenueManagerCompanyDetails

    @field_validator("full_name")
    def validate_name(cls, value):
        if not re.match(NAME_REGEX, value):
            raise ValueError("Invalid full name format")
        return value

    @field_validator("user_name")
    def validate_username(cls, value):
        if not re.match(USERNAME_REGEX, value):
            raise ValueError("Invalid user_name format")
        return value

    @field_validator("phone_number")
    def validate_phone(cls, value):
        if not re.match(PHONE_NUMBER_REGEX, value):
            raise ValueError("Invalid phone number format")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                "Password must be 8-32 characters, include uppercase, lowercase, digit, and special character"
            )
        return value

class SeatBookedByVenueManager(BaseModel,extra='forbid'):
    show_slot_id: str = Field(
        ...,
        description="Show Slot identifier",
        examples=["68c440b74afbd8670b3d0b43"]
    )
    event_id: str = Field(
        ...,
        description="Event identifier",
        examples=["68c440604afbd8670b3d0b41"]
    )
    event_title: str = Field(
        ...,
        min_length=1,
        description="Event title",
        examples=["Avatar: Fire and Ash"]
    )
    venue_id: str = Field(
        ...,
        description="Venue identifier",
        examples=["68810805c15a0fd9ebd20bc0"]
    )
    venue_name: str = Field(
        ...,
        min_length=2,
        description="Venue name",
        examples=["INOX Vega City"]
    )
    screen_name: str = Field(
        ...,
        min_length=2,
        description="Screen identifier",
        examples=["Screen 1"]
    )
    date: str = Field(
        ...,
        description="Show date (YYYY-MM-DD)",
        examples=["2025-12-19"]
    )
    language: str = Field(
        ...,
        min_length=1,
        description="Language of the movie/show",
        examples=["English"]
    )
    show_time: str = Field(
        ...,
        pattern=r"^\d{2}:\d{2}:\d{2}$",
        description="Show time in HH:MM:SS format",
        examples=["09:00:00"]
    )
    seats: List[str] = Field(
        ...,
        min_items=1,
        description="List of seat identifiers to block as offline booked",
        examples=[["A4", "A5", "A6"]]
    )

    @field_validator("show_slot_id", "event_id", "venue_id")
    def validate_object_ids(cls, value, field):
        if not re.match(OBJECT_ID_REGEX, value):
            raise ValueError(f"Invalid {field.name}: must be a 24-character hex string")
        return value
    
    @field_validator("seats")
    def validate_seats(cls, value):
        invalid = [s for s in value if not re.match(SEAT_REGEX, s)]
        if invalid:
            raise ValueError(f"Invalid seat IDs: {invalid}")
        return value