from uuid import UUID

from fastapi import HTTPException
from firebase_admin import auth
from firebase_admin.auth import UserRecord
from starlette import status

from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.tables.Feedback import Feedback
from src.db.tables.payment import Payment
from src.db.tables.ratings import Rating
from src.db.tables.user import User
from src.db.views.payment import PaymentDetails
from src.db.views.rate import RatingView
from src.responses.user import (
    PaymentResponse,
    RatingRequest,
    RatingResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.responses.util import DurationRequest
from src.utils.enums import UserType


class UserService:
    @classmethod
    def fetch_user(cls, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
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
            email=request.email,
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
            user.id = user_firebase.custom_claims[firebase_client.user_key]
        else:
            auth.set_custom_user_claims(
                request.firebase_user_id,
                {firebase_client.user_key: str(user.id)},
                app=firebase_client.app,
            )
        try:
            cockroach_client.query(
                User.add,
                items=[user],
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already found"
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
        cls, user_id: UUID, cockroach_client: CockroachDBClient
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
                count=rate.count,
            )

    @classmethod
    def get_payments(
        cls, user: User, cockroach_client: CockroachDBClient, request: DurationRequest
    ) -> list[PaymentResponse]:
        field = "receiver_id" if user.user_type == UserType.employee else "sender_id"
        payments: list[PaymentDetails] | None = cockroach_client.query(
            PaymentDetails.get_by_time_field_multiple,
            time_field="created_at",
            start_time=request.start_time,
            end_time=request.end_time,
            field=field,
            match_value=user.id,
            error_not_exist=False,
        )
        if payments is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No Payments Found"
            )
        return [
            PaymentResponse(
                id=payment.id,
                amount=payment.amount,
                created_at=payment.created_at,
                from_user=UserResponse(
                    id=payment.sender_id,
                    name=payment.sender_name,
                    phone_no=payment.sender_phone,
                    email=payment.sender_email,
                    user_type=payment.sender_user_type,
                ),
                to_user=UserResponse(
                    id=payment.receiver_id,
                    name=payment.receiver_name,
                    phone_no=payment.receiver_phone,
                    email=payment.receiver_email,
                    user_type=payment.receiver_user_type,
                ),
                currency=payment.currency,
                remarks=payment.remarks,
                approved_at=payment.approved_at,
            )
            for payment in payments
        ]

    @classmethod
    def add_feedback(
        cls, user: User, request: RatingRequest, cockroach_client: CockroachDBClient
    ) -> None:
        cockroach_client.query(
            Feedback.add,
            items=[
                Feedback(
                    from_user_id=user.id, rating=request.rate, feedback=request.comment
                )
            ],
        )

    @classmethod
    def fetch_user_by_id(
        cls, user_id: UUID, cockroach_client: CockroachDBClient
    ) -> UserResponse:
        user: User | None = cockroach_client.query(
            User.get_id, id=user_id, error_not_exist=False
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return cls.fetch_user(user)

    @classmethod
    def update_user(
        cls, user: User, request: UserUpdateRequest, cockroach_client: CockroachDBClient
    ):
        if request.email is not None and request.email != user.email:
            temp = cockroach_client.query(
                User.get_by_field_unique,
                field="email",
                match_value=request.email,
                error_not_exist=False,
            )
            if temp is not None and temp.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
                )
            user.email = request.email
        if request.phone_no is not None and request.phone_no != user.phone_no:
            temp = cockroach_client.query(
                User.get_by_field_unique,
                field="phone_no",
                match_value=request.phone_no,
                error_not_exist=False,
            )
            if temp is not None and temp.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Phone number already exists",
                )
            user.phone_no = request.phone_no
        if request.name is not None and request.name != user.name:
            user.name = request.name
        cockroach_client.query(
            User.update_by_id,
            id=user.id,
            new_data=user,
        )
