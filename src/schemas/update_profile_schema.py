from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re
from datetime import date, timedelta
from src.schemas.registration_schema import NAME_REGEX, USERNAME_REGEX, EMAIL_REGEX, PHONE_NUMBER_REGEX, ORGANIZATION_NAME_REGEX, ORGANIZATION_PAN_REGEX, PASSWORD_REGEX

class organization_details_update(BaseModel):
    """
    Model for updating details of an organization.
    """
    organization_name : Optional[str] = Field(
        None,
        min_length=3,
        description="Represents the name of the organization or company associated with the organizer."
    )
    organization_address : Optional[str] =  Field(
        None,
        min_length=5,
        description="Represents the address of the organization or company."
    )
    organization_pan_card_number : Optional[str] = Field(
        None,
        min_length=10,
        max_length=10,
        description="Represents the unique PAN deatils of the organization or company."
    )

    @field_validator("organization_name")
    def validate_organization_name(cls, value):
        if not re.match(ORGANIZATION_NAME_REGEX, value):
            raise ValueError("Invalid organization name format")
        return value
    
    @field_validator("organization_pan_card_number")
    def validate_organization_pan_card_number(cls, value):
        if not re.match(ORGANIZATION_PAN_REGEX, value):
            raise ValueError("Invalid PAN card number format")
        return value


class organizer_profile_update(BaseModel, extra = 'forbid'):
    """
    Model for updating profile information of an organizer.
    """
    name : Optional[str] = Field(
        None,
        min_length=3,
        description="Represents the name of the organizer."
    )
    # TODO enable this if needed in future
    # user_name : Optional[str] = Field(
    #     None,
    #     min_length=3,
    #     description="Represents the unique username chosen by the organizer for logging into their account."
    # )
    email : Optional[EmailStr] = Field(
        None,
        min_length=10,
        description="Represents the email address of the organizer."
    )
    phone_number : Optional[str] = Field(
        None,
        min_length=10,
        max_length=10,
        description="Represents the phone number of the organizer."
    )
    
    organization_details : Optional[organization_details_update] = None

    @field_validator("name")
    def name_validator(cls, value):
        if not re.match(NAME_REGEX, value):
            raise ValueError("Invalid name format")
        return value
    # TODO enable this if needed in future
    # @field_validator("user_name")
    # def username_validator(cls, value):
    #     if not re.match(USERNAME_REGEX, value):
    #         raise ValueError("Invalid username format")
    #     return value
    
    @field_validator("email")
    def email_validator(cls, value):
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(PHONE_NUMBER_REGEX, value):
            raise ValueError("Invalid phone number format")
        return value


class update_user_details(BaseModel, extra = 'forbid'):
    "Model for updating user credentials"
    name : Optional[str] = Field(
        None,
        min_length=3,
        examples=["John Doe"],
        description="Full name of the user."
        )
    email : Optional[EmailStr] = Field(
        None,
        min_length=10,
        examples=["john@gmail.com"],
        description="Email address for communication and login."
        )
    phone_number : Optional[str] = Field(
        None,
        description="A contact number for communication and verification purposes."
        )
    date_of_birth : Optional[date] = Field(
        None,
        description="To verify the user's age for age-restricted content or offers."
    )
    address : Optional[str] = Field(
        None,
        examples=["Bangalore"],
        description="The user's address or region for regional services or offers."
        )
    
    @field_validator("name")
    def name_validator(cls, value):
        if not re.match(NAME_REGEX, value):
            raise ValueError("Invalid name format")
        return value

    @field_validator("email")
    def email_validator(cls, value):
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(PHONE_NUMBER_REGEX, value):
            raise ValueError("Invalid phone number format")
        return value

    @field_validator("date_of_birth")
    def date_of_birth_validator(cls, value):
        if value >= date.today():
            raise ValueError("Date of birth cannot be today or in the future")
        ten_years_ago = date.today() - timedelta(days=10*365)  # Roughly 10 years ago
        if value > ten_years_ago:
            raise ValueError("User must be at least 10 years old")
        return value
