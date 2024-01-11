from typing import Type

from src.db.base import Base, DBSchemaBase
from src.utils.enums import AuthType


class User(DBSchemaBase):
    email: str
    name: str
    firebase_user_id: str
    auth_type: AuthType

    @classmethod
    def _schema_cls(cls) -> Type[Base]:
        return _User


_User = Base.from_schema_base(User, "user_accounts")
