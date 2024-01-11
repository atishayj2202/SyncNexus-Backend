from fastapi import HTTPException
from firebase_admin import auth
from firebase_admin.auth import UserRecord
from starlette import status

from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.user import User
from src.responses.user import UserCreateRequest, UserResponse


class UserService:

    @classmethod
    def fetch_user(cls, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            auth_type=user.auth_type,
            created_at=user.created_at,
        )

    @classmethod
    def create_user(
        cls, request: UserCreateRequest, cockroach_client: CockroachDBClient, firebase_client: FirebaseClient
    ) -> None:
        user: User = User(
            email=request.email,
            name=request.name,
            auth_type=request.auth_type,
            firebase_user_id=request.firebase_user_id,
        )
        user_firebase: UserRecord = auth.get_user(
            request.firebase_user_id, app=firebase_client.app
        )
        if (
            user_firebase.custom_claims is not None
            and firebase_client.user_key in user_firebase.custom_claims
        ):
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="User already exists",
            )
        try:
            cockroach_client.query(
                User.add,
                items=[user],
            )
            auth.set_custom_user_claims(
                request.firebase_user_id,
                {firebase_client.user_key: str(user.id)},
                app=firebase_client.app,
            )
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )