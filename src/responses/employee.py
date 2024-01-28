from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmployeeCreateRequest(BaseModel):
    employer_id: UUID
    employee_id: UUID
    heading: str
    description: str | None
    last_date: str | None


class EmployeeResponse(BaseModel):
    employee_id: UUID
    employer_id: UUID
    created_at: datetime | None
    last_modified_at: datetime | None


class Location(BaseModel):
    location_lat: float
    location_long: float


class LocationResponse(BaseModel):
    location: Location
    created_at: datetime | None
