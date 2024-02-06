from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.utils.enums import TaskStatus


class TaskCreateRequest(BaseModel):
    employee_id: UUID
    heading: str
    description: str | None
    last_date: datetime | None


class TaskResponse(BaseModel):
    id: UUID
    created_at: datetime
    employer_id: UUID
    employee_id: UUID
    heading: str
    description: str | None = None
    last_date: str | None = None
    status: TaskStatus
