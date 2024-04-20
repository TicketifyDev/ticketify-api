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
        min_length=5,
        examples=["john@gmail.com"],
        description="Email address for communication and login."
        )
    password : str = Field(
        min_length=4,
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

