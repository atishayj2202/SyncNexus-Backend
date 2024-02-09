from datetime import datetime
from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase


class Payment(DBSchemaBase):
    to_user_id: UUID
    from_user_id: UUID
    currency: str = "INR"
    remarks: str | None
    amount: int
    approved_at: datetime | None = None

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _Payment


_Payment = Base.from_schema_base(Payment, "payments")
