from uuid import UUID

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel
from starlette import status

from src.auth.base import _get_requesting_user
from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.employee_mapping import Employee_Mapping
from src.db.user import User


class VerifiedEmployee(BaseModel):
    employee: User
    employer: User | None = None


def employee_verify_employer(
    employee_id: UUID,
    authorization: str = Header(...),
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
):
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
        Employee_Mapping.get_by_multiple_field_unique,
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
