from datetime import datetime
from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase


class Jobs(DBSchemaBase):
    employer_id: UUID
    title: str
    description: str | None
    location_lat: float
    location_long: float
    done: datetime | None = None
    amount: int
    deleted: datetime | None = None

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _Jobs


_Jobs = Base.from_schema_base(Jobs, "jobs")
