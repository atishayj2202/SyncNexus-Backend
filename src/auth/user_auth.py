from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel

from src.auth.base import _get_requesting_user
from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.user import User


class VerifiedUser(BaseModel):
    requesting_user: User


def verify_user(
    authorization: str = Header(...),
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
) -> VerifiedUser:
    user: User = _get_requesting_user(authorization, cockroach_client, firebase_client)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return VerifiedUser(requesting_user=user)
