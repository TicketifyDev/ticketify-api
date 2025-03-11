from pydantic import BaseModel, EmailStr, Field, field_validator
from src.schemas.registration_schema import NAME_REGEX, USERNAME_REGEX, EMAIL_REGEX, PASSWORD_REGEX
from enum import Enum
import re

class RegistrationStatus(str, Enum):
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReviewRequest(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"

class AddNewAdmin(BaseModel, extra = 'forbid'):
    """
    Model for adding new admins to the application
    """
    name : str = Field(
        min_length=3,
        examples=["John Doe"],
        description="Full name of the admin."
    )
    user_name : str = Field(
        min_length=3,
        description="Unique login identifier chosen by the admin."
    )
    email : EmailStr = Field(
        min_length=10,
        examples=["john@gmail.com"],
        description="Email address for communication and login."
    )
    password : str = Field(
        min_length=8,
        max_length=32,
        description="A secure password to protect the admin's account."
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
    
    @field_validator("password")
    def password_validator(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError("Password must be at least 8-32 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character")
        return value