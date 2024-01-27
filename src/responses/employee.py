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
    created_at: str
    last_modified_at: str | datetime.time
