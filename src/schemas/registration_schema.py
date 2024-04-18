from pydantic import BaseModel, EmailStr, Field
from datetime import date

class UserRegistration(BaseModel):
    name : str = Field(min_length=3,default="John Doe")
    email : str
    password : str
    phoneNumber : str = Field(pattern="^[0-9]{10}$")
    dateOfBirth : date
    address : str = Field(default="Bangalore")

