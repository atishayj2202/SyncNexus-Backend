from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    title: str
    description: str | None
    location_lat: float
    location_long: float
    amount: int


class JobResponse(BaseModel):
    id: UUID
    created_at: datetime
    employer_id: UUID
    employee_id: UUID
    heading: str
    description: str | None = None
    last_date: str | None = None


class LocationRequest(BaseModel):
    employer_id: UUID
    location_lat: float
    location_long: float


class LocationResponse(BaseModel):
    employer_id: UUID
    location_lat: float
    location_long: float
