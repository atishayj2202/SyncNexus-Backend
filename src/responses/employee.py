from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.utils.enums import EmployeeStatus


class EmployeeResponse(BaseModel):
    employee_id: UUID
    name: str
    phone_no: str
    status: EmployeeStatus
