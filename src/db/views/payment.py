from datetime import datetime
from typing import Type
from uuid import UUID

from src.db.base import Base, DBSchemaBase
from src.utils.enums import UserType


class PaymentDetails(DBSchemaBase):
    sender_id: UUID
    sender_name: str
    sender_phone: str
    sender_email: str | None = None
    sender_user_type: UserType
    receiver_id: UUID
    receiver_name: str
    receiver_phone: str
    receiver_email: str | None = None
    receiver_user_type: UserType
    currency: str = "INR"
    remarks: str | None
    amount: int
    approved_at: datetime | None = None

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _PaymentDetails


_PaymentDetails = Base.from_schema_base(PaymentDetails, "payment_details")
