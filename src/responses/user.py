from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.utils.enums import UserType


class UserResponse(BaseModel):
    id: UUID
    name: str
    phone_no: str
    email: str | None = None
    created_at: datetime | None = None
    user_type: UserType


class UserCreateRequest(BaseModel):
    email: str | None = None
    phone_no: str
    name: str
    user_type: UserType
    firebase_user_id: str


class UserUpdateRequest(BaseModel):
    email: str | None = None
    phone_no: str | None = None
    name: str | None = None


class RatingRequest(BaseModel):
    rate: int
    comment: str | None = None


class RatingResponse(BaseModel):
    rate: int
    comment: str | None = None
    count: int


class PaymentRequest(BaseModel):
    amount: int
    currency: str = "INR"
    remarks: str | None = None


class PaymentResponse(BaseModel):
    id: UUID
    amount: int
    from_user: UserResponse
    to_user: UserResponse
    currency: str = "INR"
    remarks: str | None = None
    created_at: datetime
    approved_at: datetime | None = None
