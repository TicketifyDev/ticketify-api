from pydantic import BaseModel, EmailStr, Field
from datetime import date

class user_registration(BaseModel):
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
        pattern="^[0-9]{10}$",
        description="A contact number for communication and verification purposes."
        )
    date_of_birth : date = Field(
        description="To verify the user's age for age-restricted content or offers."
    )
    address : str = Field(
        examples=["Bangalore"],
        description="The user's address or region for regional services or offers."
        )


class organization_details(BaseModel):
    organization_name : str = Field(
        min_length=3,
        examples=["EventPro Solutions"],
        description="Represents the name of the organization or company associated with the organizer.",
        title="Full name"
    )
    organization_address : str =  Field(
        min_length=5,
        examples=["Bangalore"],
        description="Represents the address of the organization or company."
    )
    organization_pan_card_number : str = Field(
        min_length=10,
        max_length=10,
        pattern="^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
        examples=["ABCPD1234E"],
        description="Represents the unique PAN deatils of the organization or company."
    )

class organizer_registration(BaseModel):
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
        pattern="^[0-9]{10}$",
        description="Represents the phone number of the organizer."
    )
    password : str = Field(
        min_length=8,
        max_length=32,
        description="Represents the password chosen by the organizer for their account."
    )
    organization_details : organization_details

    
