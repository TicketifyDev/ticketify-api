from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, timedelta
import re

#Constants for Regex Patterns
NAME_REGEX = r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$"
USERNAME_REGEX = r"^[a-zA-Z0-9_.]+$"
EMAIL_REGEX = r"^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,3})+$"
PHONE_NUMBER_REGEX = r"^[6-9]\d{9}$"
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$"
ORGANIZATION_NAME_REGEX = r"^[A-Za-z0-9À-ÖØ-öø-ÿ' -]+$"
ORGANIZATION_PAN_REGEX = r"^[A-Z]{5}\d{4}[A-Z]$"


class user_registration(BaseModel, extra = 'forbid'):
    """
    Model representing the registration data required for creating a new user account.
    """
    name : str = Field(
        min_length=3,
        examples=["John Doe"],
        description="Full name of the user."
        )
    user_name : str = Field(
        min_length=3,
        description="Unique login identifier chosen by the user."
        )
    email : EmailStr = Field(
        min_length=10,
        examples=["john@gmail.com"],
        description="Email address for communication and login."
        )
    password : str = Field(
        min_length=8,
        max_length=32,
        description="A secure password to protect the user's account."
        )
    phone_number : str = Field(
        description="A contact number for communication and verification purposes."
        )
    date_of_birth : date = Field(
        description="To verify the user's age for age-restricted content or offers."
    )
    address : str = Field(
        examples=["Bangalore"],
        description="The user's address or region for regional services or offers."
        )
    
    @field_validator("name")
    def name_validator(cls, value):
        if not re.match(NAME_REGEX, value):
            raise ValueError("Invalid name format")
        return value

    @field_validator("user_name")
    def username_validator(cls, value):
        if not re.match(USERNAME_REGEX, value):
            raise ValueError("Invalid username format")
        return value
    
    @field_validator("email")
    def email_validator(cls, value):
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("date_of_birth")
    def date_of_birth_validator(cls, value):
        if value >= date.today():
            raise ValueError("Date of birth cannot be today or in the future")
        ten_years_ago = date.today() - timedelta(days=10*365)  # Roughly 10 years ago
        if value > ten_years_ago:
            raise ValueError("User must be at least 10 years old")
        return value
    
    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(PHONE_NUMBER_REGEX, value):
            raise ValueError("Invalid phone number format")
        return value

    @field_validator("password")
    def password_validator(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError("Password must be at least 8-32 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character")
        return value

class organization_details(BaseModel, extra = 'forbid'):
    """
    Model representing additional details about an organization or company.
    """
    organization_name : str = Field(
        min_length=3,
        examples=["EventPro Solutions"],
        description="Represents the name of the organization or company associated with the organizer."
    )
    organization_address : str =  Field(
        min_length=5,
        examples=["Bangalore"],
        description="Represents the address of the organization or company."
    )
    organization_pan_card_number : str = Field(
        min_length=10,
        max_length=10,
        examples=["ABCPD1234E"],
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

class organizer_registration(BaseModel, extra = 'forbid'):
    """
    Model representing the registration data required for creating a new organizer account.
    """
    name : str = Field(
        min_length=3,
        examples=["John Doe"],
        description="Represents the name of the organizer."
    )
    user_name : str = Field(
        min_length=3,
        examples=["john_doe"],
        description="Represents the unique username chosen by the organizer for logging into their account."
    )
    email : EmailStr = Field(
        min_length=10,
        examples=["john@gmail.com"],
        description="Represents the email address of the organizer."
    )
    phone_number : str = Field(
        min_length=10,
        max_length=10,
        description="Represents the phone number of the organizer."
    )
    password : str = Field(
        min_length=8,
        max_length=32,
        description="Represents the password chosen by the organizer for their account."
    )
    organization_details : organization_details

    @field_validator("name")
    def name_validator(cls, value):
        if not re.match(NAME_REGEX, value):
            raise ValueError("Invalid name format")
        return value

    @field_validator("user_name")
    def username_validator(cls, value):
        if not re.match(USERNAME_REGEX, value):
            raise ValueError("Invalid username format")
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

    @field_validator("password")
    def password_validator(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError("Password must be at least 8-32 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character")
        return value