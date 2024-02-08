from typing import Type

from src.db.base import Base, DBSchemaBase
from src.utils.enums import UserType


class User(DBSchemaBase):
    phone_no: str
    email: str | None
    name: str
    firebase_user_id: str
    user_type: UserType

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _User


_User = Base.from_schema_base(User, "user_accounts")
