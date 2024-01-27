from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    employer_id: UUID
    title: str
    description: str | None
    location_lat: float
    location_long: float
    done: str | None
    amount: int
    deleted: datetime | None = None


class JobResponse(BaseModel):
    id: UUID
    created_at: datetime
    employer_id: UUID
    employee_id: UUID
    heading: str
    description: str | None = None
    last_date: str | None = None