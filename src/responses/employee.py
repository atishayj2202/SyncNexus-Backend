from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.utils.enums import EmployeeStatus


class EmployeeCreateRequest(BaseModel):
    employer_id: UUID
    employee_id: UUID
    heading: str
    description: str | None
    last_date: str | None


class EmployeeResponse(BaseModel):
    employee_id: UUID
    name: str
    phone_no: str
    status: EmployeeStatus


class Location(BaseModel):
    location_lat: float
    location_long: float


class LocationResponse(BaseModel):
    employee_id: UUID
    location: Location
    created_at: datetime | None
