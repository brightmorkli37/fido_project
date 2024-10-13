from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str
    created_at: datetime