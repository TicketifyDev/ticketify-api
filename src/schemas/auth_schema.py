from pydantic import BaseModel, Field

class AuthModel(BaseModel, extra = "forbid"):
    username : str = Field(min_length=1)
    password : str = Field(min_length=1)