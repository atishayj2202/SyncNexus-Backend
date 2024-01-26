from datetime import datetime
from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase


class Task(DBSchemaBase):
    employee_id: UUID
    employer_id: UUID
    heading: str
    description: str | None = None
    last_date: datetime | None = None
    deleted: datetime | None = None
    completed: datetime | None = None

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _Task


_Task = Base.from_schema_base(Task, "task")
