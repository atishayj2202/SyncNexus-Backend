from __future__ import annotations

import re
import types
import typing
import uuid
from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Type

from pydantic import BaseModel, Field
from sqlalchemy import ARRAY, JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, Integer, String, and_, func, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta, Session, declared_attr

from src.utils.time import get_current_time


def snake_case_to_camel_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Base:
    @declared_attr
    def __tablename__(cls):
        name = cls.__name__
        if name.startswith("_"):
            name = name[1:]
        return snake_case_to_camel_case(name)

    @classmethod
    def _parse_sql_alchemy_type(cls, annotation):
        if isinstance(annotation, types.UnionType):
            annotation = [
                t for t in typing.get_args(annotation) if t != types.NoneType
            ][0]
        if annotation == str:
            return String
        if annotation == int:
            return Integer
        if annotation == datetime:
            return DateTime
        if annotation == uuid.UUID:
            return UUID(as_uuid=True)
        if annotation == bool:
            return Boolean
        if annotation == float:
            return Float
        if typing.get_origin(annotation) == dict:
            return JSON
        if typing.get_origin(annotation) == list:
            return ARRAY(UUID)
        if issubclass(annotation, Enum):
            return SQLEnum(annotation)
        raise Exception(f"Type {annotation} not supported")

    @classmethod
    def from_schema_base(
        cls, base: Type[DBSchemaBase], override_table_name: Optional[str] = None
    ) -> type:
        default_fields = base._default_sql_alchemy_fields()
        new_fields = {
            name: Column(
                cls._parse_sql_alchemy_type(f.annotation),
                nullable=f.is_required(),
                default=f.default,
            )
            for name, f in base.model_fields.items()
            if name not in default_fields
        }
        table_name = override_table_name or snake_case_to_camel_case(base.__name__)
        return type(table_name, (Base,), {**new_fields, **default_fields})


Base: DeclarativeMeta = declarative_base(cls=Base)


class DBSchemaBase(BaseModel, ABC):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    # default values for timestamps are handled at database level
    created_at: datetime = Field(default_factory=get_current_time)
    last_modified_at: datetime = Field(default_factory=get_current_time)

    _cached_schema_cls = None

    @classmethod
    def _fixed_fields(cls):
        return {"id", "created_at"}

    @classmethod
    def _default_sql_alchemy_fields(cls):
        return {
            "id": Column(
                UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
            ),
            "created_at": Column(DateTime, default=func.now(), nullable=False),
            "last_modified_at": Column(DateTime, default=func.now(), nullable=False),
        }

    @classmethod
    def add(cls, db: Session, items: List[DBSchemaBase]):
        for item in items:
            po = cls._schema_cls()(**item.model_dump(exclude_none=True))
            db.add(po)

    @classmethod
    def _extract_all_data(cls, db: Session, statement) -> List[DBSchemaBase] | None:
        results = db.execute(statement).scalars().all()
        return [cls.model_validate(po, from_attributes=True) for po in results]

    @classmethod
    def get_all(cls, db: Session) -> List[DBSchemaBase] | None:
        return cls._extract_all_data(db, select(cls._schema_cls()))

    @classmethod
    def get_id(
        cls, db: Session, id: UUID, error_not_exist: bool = True
    ) -> DBSchemaBase | None:
        schema_cls = cls._schema_cls()
        result = db.query(schema_cls).filter(cls._schema_cls().id == id).first()
        if result:
            return cls.model_validate(result, from_attributes=True)
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with id {id}"
            )
        return None

    @classmethod
    def _schema_cls(cls):
        if cls._cached_schema_cls is None:
            cls._cached_schema_cls = Base.from_schema_base(cls)
        return cls._cached_schema_cls

    @classmethod
    def get_multiple_in_radius(
        cls,
        db: Session,
        lat: float,
        lon: float,
        radius: float,
        error_not_exist: bool = False,
    ) -> List[DBSchemaBase] | None:
        schema_cls = cls._schema_cls()
        result = (
            db.query(schema_cls)
            .filter(
                and_(
                    func.earth_box(func.ll_to_earth(lat, lon), radius).op("@>")(
                        func.ll_to_earth(
                            getattr(schema_cls, "location_lat"),
                            getattr(schema_cls, "location_long"),
                        )
                    )
                )
            )
            .all()
        )
        if result:
            return [cls.model_validate(r, from_attributes=True) for r in result]
        if error_not_exist:
            raise Exception(f"Could not find a record in {schema_cls.__name__}")
        return None

    @classmethod
    def get_by_field_unique(
        cls, db: Session, field: str, match_value: Any, error_not_exist: bool = False
    ) -> DBSchemaBase | None:
        """generic function to extract a single record which matches given column and value condition"""
        schema_cls = cls._schema_cls()
        result = (
            db.query(schema_cls)
            .filter(and_(getattr(schema_cls, field) == match_value))
            .first()
        )
        if result:
            return cls.model_validate(result, from_attributes=True)
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with {field} {match_value}"
            )
        return None

    @classmethod
    def get_by_multiple_field_unique(
        cls,
        db: Session,
        fields: list[str],
        match_values: list[Any],
        error_not_exist: bool = False,
    ) -> DBSchemaBase | None:
        schema_cls = cls._schema_cls()
        result = (
            db.query(schema_cls)
            .filter(
                and_(
                    *(getattr(schema_cls, f) == v for f, v in zip(fields, match_values))
                )
            )
            .first()
        )
        if result:
            return cls.model_validate(result, from_attributes=True)
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with {fields} {match_values}"
            )
        return None

    @classmethod
    def get_by_multiple_field_multiple(
        cls,
        db: Session,
        fields: list[str],
        match_values: list[Any],
        error_not_exist: bool = False,
    ) -> list[DBSchemaBase] | None:
        schema_cls = cls._schema_cls()
        result = (
            db.query(schema_cls)
            .filter(
                and_(
                    *(getattr(schema_cls, f) == v for f, v in zip(fields, match_values))
                )
            )
            .all()
        )
        if result:
            return [cls.model_validate(r, from_attributes=True) for r in result]
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with {fields} {match_values}"
            )
        return None

    @classmethod
    def get_by_field_multiple(
        cls, db: Session, field: str, match_value: Any, error_not_exist: bool = False
    ) -> list[DBSchemaBase] | None:
        """generic function to extract a single record which matches given column and value condition"""
        schema_cls = cls._schema_cls()
        result = (
            db.query(schema_cls)
            .filter(and_(getattr(schema_cls, field) == match_value))
            .all()
        )
        if result:
            return [cls.model_validate(r, from_attributes=True) for r in result]
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with {field} {match_value}"
            )
        return None

    @classmethod
    def get_by_time_field_multiple(
        cls,
        db: Session,
        time_field: str,
        start_time: datetime,
        end_time: datetime,
        field: str,
        match_value: Any,
        error_not_exist: bool = False,
    ) -> list[DBSchemaBase] | None:
        schema_cls = cls._schema_cls()
        result = (
            db.query(schema_cls)
            .filter(
                and_(
                    getattr(schema_cls, field) == match_value,
                    getattr(schema_cls, time_field).between(start_time, end_time),
                )
            )
            .all()
        )
        if result:
            return [cls.model_validate(r, from_attributes=True) for r in result]
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with {field} {match_value}"
            )
        return None

    @classmethod
    def get_by_field_value_list(
        cls,
        db: Session,
        field: str,
        match_values: list[Any],
        error_not_exist: bool = False,
    ) -> list[DBSchemaBase] | None:
        """generic function to extract a single record which matches given column and value condition"""
        schema_cls = cls._schema_cls()
        result = (
            db.query(schema_cls)
            .filter(getattr(schema_cls, field).in_(match_values))
            .all()
        )
        if result:
            return [cls.model_validate(r, from_attributes=True) for r in result]
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with {field} being one of {match_values}"
            )
        return None

    @classmethod
    def update_by_id(cls, db: Session, id: UUID, new_data: DBSchemaBase):
        # Retrieve the item by ID
        schema_cls = cls._schema_cls()
        new_data.last_modified_at = get_current_time()

        update_data = {
            key: value
            for key, value in new_data.model_dump().items()
            if key not in cls._fixed_fields()
        }
        db.query(schema_cls).filter(cls._schema_cls().id == id).update(update_data)

    @classmethod
    def get_field(cls, field):
        schema_cls = cls._schema_cls()
        return getattr(schema_cls, field)

    @classmethod
    def get_latest_record(
        cls,
        db: Session,
        field: str,
        match_value: Any,
        model_field: Any,
        error_not_exist: bool = False,
    ) -> DBSchemaBase | None:
        """generic function to extract a single record which matches given column and value condition"""
        schema_cls = cls._schema_cls()
        model_column = cls.get_field(model_field)
        result = (
            db.query(schema_cls)
            .filter(and_(getattr(schema_cls, field) == match_value))
            .order_by(model_column.desc())
            .first()
        )
        if result:
            return cls.model_validate(result, from_attributes=True)
        if error_not_exist:
            raise Exception(
                f"Could not find a record in {schema_cls.__name__} with {field} {match_value}"
            )
        return None

    @classmethod
    def delete_by_id(cls, db: Session, id: UUID):
        schema_cls = cls._schema_cls()
        db.query(schema_cls).filter(cls._schema_cls().id == id).delete()
