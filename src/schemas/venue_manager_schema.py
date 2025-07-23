from pydantic import BaseModel, EmailStr, Field, field_validator
import re


#Constants for Regex Patterns
NAME_REGEX = r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$"
USERNAME_REGEX = r"^[a-zA-Z0-9_.]+$"
EMAIL_REGEX = r"^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,3})+$"
PHONE_NUMBER_REGEX = r"^[6-9]\d{9}$"
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$"
GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

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
