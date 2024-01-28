from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth import user_auth
from src.auth.user_auth import VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.responses.user import UserCreateRequest, UserResponse
from src.services.user import UserService

USER_PREFIX = "/user"
user_router = APIRouter(prefix=USER_PREFIX)
ENDPOINT_CREATE_USER = "/create-user/"  # done
ENDPOINT_GET_USER = "/{user_id}/get-user/"  # done
ENDPOINT_GET_USER_LOGS = "/{user_id}/get-user-logs/"  # pending
ENDPOINT_ADD_RATING = "/{user_id}/add-rating/"  # pending
ENDPOINT_GET_RATING = "/{user_id}/get-rating/"  # pending


@user_router.post(ENDPOINT_CREATE_USER)
async def post_create_user(
    request: UserCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    firebase_client: FirebaseClient = Depends(),
):
    UserService.create_user(request, cockroach_client, firebase_client)
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(ENDPOINT_GET_USER, response_model=UserResponse)
async def get_user(
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    return UserService.fetch_user(verified_user.requesting_user)


@user_router.get(ENDPOINT_GET_USER_LOGS, response_model=UserResponse)
async def get_user_logs(
        verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    return UserService.fetch_user_logs(verified_user.requesting_user)


@user_router.post(ENDPOINT_ADD_RATING)
async def post_create_rating(
        request: UserCreateRequest,
        cockroach_client: CockroachDBClient = Depends(),
        firebase_client: FirebaseClient = Depends(),
):
    UserService.create_rating(request, cockroach_client, firebase_client)
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(ENDPOINT_GET_RATING, response_model=UserResponse)
async def get_user(
        verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    return UserService.fetch_rating(verified_user.requesting_user)
