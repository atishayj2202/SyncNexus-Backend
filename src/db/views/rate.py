from typing import Type

from src.db.base import Base, DBSchemaBase


class RatingView(DBSchemaBase):
    rate: float
    count: int

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _RatingView


_RatingView = Base.from_schema_base(RatingView, "avg_rating_with_comments")
