from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    full_name: str

class UserResponse(BaseModel):
    id: str
    full_name: str
    created_at: Optional[datetime] = None
