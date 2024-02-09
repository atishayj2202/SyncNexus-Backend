from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase


class Feedback(DBSchemaBase):
    from_user_id: UUID
    feedback: str | None
    rating: int

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _Feedback


_Feedback = Base.from_schema_base(Feedback, "feedbacks")
