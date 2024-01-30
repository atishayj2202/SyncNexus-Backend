from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase


class Rating(DBSchemaBase):
    user_to: UUID
    user_from: UUID
    rate: int
    comment: str | None = None

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _Rating


_Rating = Base.from_schema_base(Rating, "rating")
