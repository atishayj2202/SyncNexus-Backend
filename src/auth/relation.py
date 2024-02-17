from uuid import UUID

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel
from starlette import status

from src.auth.base import _get_requesting_user
from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.tables.employee_mapping import EmployeeMapping
from src.db.tables.user import User
from src.utils.client import getCockroachClient, getFirebaseClient
from src.utils.enums import UserType


class VerifiedEmployee(BaseModel):
    employee: User
    employer: User | None = None


class VerifiedEmployer(BaseModel):
    employer: User
    employee: User | None = None


def verify_employee_s_employer(
    employee_id: UUID,
    authorization: str = Header(...),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    firebase_client: FirebaseClient = Depends(getFirebaseClient),
) -> VerifiedEmployee:
    user: User = _get_requesting_user(authorization, cockroach_client, firebase_client)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if employee_id == user.id or user.user_type == UserType.employee:
        return VerifiedEmployee(employee=user, employer=None)
    employee = cockroach_client.query(
        User.get_id,
        id=employee_id,
        error_not_exist=False,
    )
    if employee is None:
        raise HTTPException(status_code=401, detail="Employee not found")
    employee_mapping = cockroach_client.query(
        EmployeeMapping.get_by_multiple_field_unique,
        fields=["employee_id", "employer_id", "deleted"],
        match_values=[employee_id, user.id, None],
        error_not_exist=False,
    )
    if employee_mapping is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee not Under Employer",
        )
    return VerifiedEmployee(employee=employee, employer=user)


def verify_employer_s_employee(
    employer_id: UUID,
    authorization: str = Header(...),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    firebase_client: FirebaseClient = Depends(getFirebaseClient),
) -> VerifiedEmployer:
    user: User = _get_requesting_user(authorization, cockroach_client, firebase_client)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if employer_id == user.id or user.user_type == UserType.employer:
        return VerifiedEmployer(employee=None, employer=user)
    employer = cockroach_client.query(
        User.get_id,
        id=employer_id,
        error_not_exist=False,
    )
    if employer is None:
        raise HTTPException(status_code=401, detail="Employee not found")
    employee_mapping = cockroach_client.query(
        EmployeeMapping.get_by_multiple_field_unique,
        fields=["employee_id", "employer_id", "deleted"],
        match_values=[user.id, employer.id, None],
        error_not_exist=False,
    )
    if employee_mapping is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee not Under Employer",
        )
    return VerifiedEmployer(employee=user, employer=employer)
