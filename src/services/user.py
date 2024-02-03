from uuid import UUID

from fastapi import HTTPException
from firebase_admin import auth
from firebase_admin.auth import UserRecord
from starlette import status

from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.tables.ratings import Rating
from src.db.tables.user import User
from src.db.views.rate import RatingView
from src.responses.user import (
    RatingRequest,
    RatingResponse,
    UserCreateRequest,
    UserResponse,
)


class UserService:
    @classmethod
    def fetch_user(cls, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            name=user.name,
            phone_no=user.phone_no,
            user_type=user.user_type,
            created_at=user.created_at,
        )

    @classmethod
    def create_user(
        cls,
        request: UserCreateRequest,
        cockroach_client: CockroachDBClient,
        firebase_client: FirebaseClient,
    ) -> None:
        user: User = User(
            phone_no=request.phone_no,
            name=request.name,
            user_type=request.user_type,
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

    @classmethod
    def create_rating(
        cls,
        user_from: User,
        user_to_id: UUID,
        request: RatingRequest,
        cockroach_client: CockroachDBClient,
    ) -> None:
        rate = Rating(
            user_to=user_to_id,
            user_from=user_from.id,
            rate=request.rate,
            comment=request.comment,
        )
        temp = cockroach_client.query(
            Rating.get_by_multiple_field_unique,
            fields=["user_to", "user_from"],
            match_values=[user_to_id, user_from.id],
            error_not_exist=False,
        )
        if temp is not None:
            temp.rate = request.rate
            temp.comment = request.comment
            cockroach_client.query(
                Rating.update_by_id,
                id=temp.id,
                new_data=temp,
            )
        else:
            cockroach_client.query(
                Rating.add,
                items=[rate],
            )

    @classmethod
    def fetch_rating(
        cls, user_id: User, cockroach_client: CockroachDBClient
    ) -> RatingResponse:
        rate = cockroach_client.query(
            RatingView.get_id,
            id=user_id,
            error_not_exist=False,
        )
        if rate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found"
            )
        else:
            return RatingResponse(
                rate=rate.rate,
                comment=rate.comment,
                count=rate.count,
            )
