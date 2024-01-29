from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.utils.enums import UserType


class UserResponse(BaseModel):
    id: UUID
    name: str
    phone_no: str
    created_at: datetime
    user_type: UserType


class UserCreateRequest(BaseModel):
    phone_no: str
    name: str
    user_type: UserType
    firebase_user_id: str
