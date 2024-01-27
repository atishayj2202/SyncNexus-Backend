import os
import random
from typing import List
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from firebase_admin import auth
from firebase_admin.auth import UserRecord

from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.user import User
from src.main import app
from src.utils.enums import UserType


@pytest.fixture(scope="session")
def cockroach_client():
    return CockroachDBClient(url=os.environ["COCKROACH_DB_LOCAL_URL"])


@pytest.fixture(scope="session")
def firebase_client():
    return FirebaseClient()


@pytest.fixture(scope="function")
def make_random_email(cockroach_client):
    def fn():
        email = "abc" + str(random.randint(100, 10000)) + "@gmail.com"
        user = cockroach_client.query(
            User.get_by_field_unique,
            field="phone_no",
            match_value=email,
        )
        if user is not None:
            return fn()
        return email

    return fn


@pytest.fixture(scope="session")
def app_test_client():
    return TestClient(app)


@pytest.fixture(scope="session")
def fast_api_auth_header_random_employee(
    firebase_client, make_random_email, cockroach_client
) -> tuple[User, dict]:
    email = make_random_email()
    password = "omjALeay"
    firebase_user = firebase_client.create_user(email, password)
    user = User(
        id=uuid4(),
        type=UserType.employee,
        email=email,
        firebase_user_id=str(firebase_user.uid),
    )
    cockroach_client.query(
        User.add,
        items=[user],
    )
    yield user, {
        "Authorization": f"Bearer {firebase_client.get_user_token(firebase_user.uid)}"
    }
    firebase_client.delete_user(firebase_user.uid)


@pytest.fixture(scope="session")
def fast_api_auth_header_random_employer(
    firebase_client, make_random_email, cockroach_client
) -> tuple[User, dict]:
    email = make_random_email()
    password = "omjALeay"
    firebase_user = firebase_client.create_user(email, password)
    user = User(
        id=uuid4(),
        type=UserType.employer,
        email=email,
        firebase_user_id=str(firebase_user.uid),
    )
    cockroach_client.query(
        User.add,
        items=[user],
    )
    yield user, {
        "Authorization": f"Bearer {firebase_client.get_user_token(firebase_user.uid)}"
    }
    firebase_client.delete_user(firebase_user.uid)
