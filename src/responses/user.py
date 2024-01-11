from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.utils.enums import AuthType


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime
    auth_type: AuthType


class UserCreateRequest(BaseModel):
    email: str
    name: str
    auth_type: AuthType
    firebase_user_id: str
