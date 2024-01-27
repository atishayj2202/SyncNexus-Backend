from uuid import UUID

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel
from starlette import status

from src.auth.base import _get_requesting_user
from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.task import Task
from src.db.user import User


class VerifiedUser(BaseModel):
    requesting_user: User


class VerifiedTask(BaseModel):
    task: Task
    requesting_user: User


def verify_user(
    authorization: str = Header(...),
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
) -> VerifiedUser:
    user: User = _get_requesting_user(authorization, cockroach_client, firebase_client)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return VerifiedUser(requesting_user=user)


def verify_task(
    task_id: UUID,
    authorization: str = Header(...),
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
):
    user: User = _get_requesting_user(authorization, cockroach_client, firebase_client)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    task: Task = cockroach_client.query(
        Task.get_id,
        id=task_id,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    if task.employee_id != user.id and task.employer_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return VerifiedTask(task=task, requesting_user=user)
