from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase


class EmployeeLocation(DBSchemaBase):
    employee_id: UUID
    location_lat: float
    location_long: float

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _EmployeeLocation


_EmployeeLocation = Base.from_schema_base(EmployeeLocation, "employee_location")
