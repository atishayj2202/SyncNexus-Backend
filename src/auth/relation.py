from uuid import UUID

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel
from starlette import status

from src.auth.base import _get_requesting_user
from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.tables.employee_mapping import EmployeeMapping
from src.db.tables.user import User


class VerifiedEmployee(BaseModel):
    employee: User
    employer: User | None = None


class VerifiedEmployer(BaseModel):
    employer: User
    employee: User | None = None


def verify_employee_s_employer(
    employee_id: UUID,
    authorization: str = Header(...),
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
) -> VerifiedEmployee:
    user: User = _get_requesting_user(authorization, cockroach_client, firebase_client)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    employee = cockroach_client.query(
        User.get_id,
        id=employee_id,
    )
    if employee is None:
        raise HTTPException(status_code=401, detail="Employee not found")
    if employee.id == user.id:
        return VerifiedEmployee(employee=employee, employer=None)
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
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
) -> VerifiedEmployer:
    user: User = _get_requesting_user(authorization, cockroach_client, firebase_client)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    employer = cockroach_client.query(
        User.get_id,
        id=employer_id,
    )
    if employer is None:
        raise HTTPException(status_code=401, detail="Employee not found")
    if employer.id == user.id:
        return VerifiedEmployer(employee=None, employer=employer)
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
