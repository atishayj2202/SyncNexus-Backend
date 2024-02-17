from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.responses.util import Location


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
    title: str
    description: str | None = None
    location: Location
    done: datetime | None = None
    amount: int
    deleted: datetime | None = None
