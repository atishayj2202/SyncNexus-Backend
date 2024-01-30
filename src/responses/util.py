from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DurationRequest(BaseModel):
    start_time: datetime
    end_time: datetime


class Location(BaseModel):
    location_lat: float
    location_long: float


class LocationResponse(BaseModel):
    employee_id: UUID
    location: Location
    created_at: datetime | None
