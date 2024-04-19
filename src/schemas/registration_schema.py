from pydantic import BaseModel, EmailStr, Field
from datetime import date

class user_registration(BaseModel):
    name : str = Field(min_length=3,examples=["John Doe"])
    user_name : str 
    email : str
    password : str
    phone_number : str = Field(pattern="^[0-9]{10}$")
    date_of_birth : date
    address : str = Field(examples=["Bangalore"])

