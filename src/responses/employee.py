from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.utils.enums import EmployeeStatus


class EmployeeResponse(BaseModel):
    employee_id: UUID
    title: str
    name: str
    phone_no: str
    status: EmployeeStatus
    email: str
    join_date: datetime
