from datetime import datetime
from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase
from src.utils.enums import EmployeeStatus


class Employee_Mapping(DBSchemaBase):
    employee_id: UUID
    employer_id: UUID
    deleted: datetime | None = None
    status: EmployeeStatus = EmployeeStatus.active

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _Employee_Mapping


_Employee_Mapping = Base.from_schema_base(Employee_Mapping, "employee_mapping")
