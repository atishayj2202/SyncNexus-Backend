from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import Response

from src.auth import user_auth
from src.auth.user_auth import VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.responses.user import (
    PaymentResponse,
    RatingRequest,
    RatingResponse,
    UserCreateRequest,
    UserResponse,
)
from src.responses.util import DurationRequest
from src.services.user import UserService

USER_PREFIX = "/user"
user_router = APIRouter(prefix=USER_PREFIX)
ENDPOINT_CREATE_USER = "/create-user/"  # done | integrated
ENDPOINT_CHECK_USER = "/check-user/"  # done | integrated
ENDPOINT_GET_USER = "/get-user/"  # done | integrated
ENDPOINT_GET_USER_LOGS = "/{user_id}/get-user-logs/"  # deprecated
ENDPOINT_ADD_RATING = "/{user_id}/add-rating/"  # done | integrated
ENDPOINT_GET_RATING = "/{user_id}/get-rating/"  # done | integrated
ENDPOINT_GET_PAYMENTS = "/get-payments/"  # done | integrated
ENDPOINT_ADD_FEEDBACK = "/add-feedback/"  # done | integrated


@user_router.post(ENDPOINT_CREATE_USER)
async def post_create_user(
    request: UserCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
):
    UserService.create_user(request, cockroach_client, firebase_client)
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(
    ENDPOINT_CHECK_USER,
    dependencies=[Depends(user_auth.verify_user)],
)
async def get_check_user():
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(ENDPOINT_GET_USER, response_model=UserResponse)
async def get_user(
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    return UserService.fetch_user(verified_user.requesting_user)


@user_router.post(ENDPOINT_ADD_RATING)
async def post_create_rating(
    user_id: UUID,
    request: RatingRequest,
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
    cockroach_client: CockroachDBClient = Depends(),
):
    if user_id == verified_user.requesting_user.id:
        raise HTTPException(
            status_code=400, detail="User cannot rate themselves"
        )
    UserService.create_rating(
        user_from=verified_user.requesting_user,
        user_to_id=user_id,
        request=request,
        cockroach_client=cockroach_client,
    )
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(
    ENDPOINT_GET_RATING,
    response_model=RatingResponse,
    dependencies=[Depends(user_auth.verify_user)],
)
async def get_rating(
    user_id: UUID,
    cockroach_client: CockroachDBClient = Depends(),
):
    return UserService.fetch_rating(user_id=user_id, cockroach_client=cockroach_client)


@user_router.post(
    ENDPOINT_GET_PAYMENTS,
    response_model=list[PaymentResponse],
)
async def get_payments(
    request: DurationRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    return UserService.get_payments(
        user=verified_user.requesting_user,
        cockroach_client=cockroach_client,
        request=request,
    )


@user_router.post(ENDPOINT_ADD_FEEDBACK)
async def post_add_feedback(
    request: RatingRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    UserService.add_feedback(
        user=verified_user.requesting_user,
        request=request,
        cockroach_client=cockroach_client,
    )
    return Response(status_code=status.HTTP_200_OK)
