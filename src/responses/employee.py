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
