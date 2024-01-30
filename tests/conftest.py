import os

import pytest
from fastapi.testclient import TestClient

from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.tables.user import User
from src.main import app
from src.utils.enums import UserType


@pytest.fixture(scope="session")
def cockroach_client():
    return CockroachDBClient(url=os.environ["COCKROACH_DB_LOCAL_URL"])


@pytest.fixture(scope="session")
def firebase_client():
    return FirebaseClient()


@pytest.fixture(scope="session")
def app_test_client():
    return TestClient(app)


@pytest.fixture(scope="session")
def fb_test_employer_id():
    return os.environ["FIREBASE_TEST_PHONE_1_ID"]


@pytest.fixture(scope="session")
def fb_test_employer_token(firebase_client, fb_test_employer_id):
    return firebase_client.get_user_token(uid=fb_test_employer_id)


@pytest.fixture(scope="session")
def fast_api_auth_header_employer(fb_test_employer_token):
    return {"Authorization": f"Bearer {fb_test_employer_token}"}


@pytest.fixture(scope="session")
def fb_test_employee_id():
    return os.environ["FIREBASE_TEST_PHONE_2_ID"]


@pytest.fixture(scope="session")
def fb_test_employee_phone():
    return os.environ["FIREBASE_TEST_PHONE_2"]


@pytest.fixture(scope="session")
def fb_test_employer_phone():
    return os.environ["FIREBASE_TEST_PHONE_1"]


@pytest.fixture(scope="session")
def fb_test_employee_token(firebase_client, fb_test_employee_id):
    return firebase_client.get_user_token(uid=fb_test_employee_id)


@pytest.fixture(scope="session")
def test_employee_client(
    fb_test_employee_id, cockroach_client, fb_test_employee_phone
) -> User:
    existing_users: dict[str, User] = {
        u.firebase_user_id: u for u in cockroach_client.query(User.get_all)
    }
    if fb_test_employee_id in existing_users:
        return existing_users[fb_test_employee_id]
    # create new
    user = User(
        phone_no=fb_test_employee_phone,
        name="test_user2",
        user_type=UserType.employee,
        firebase_user_id=fb_test_employee_id,
    )
    cockroach_client.query(User.add, items=[user])
    return user


def test_employer_client(
    fb_test_employer_id, cockroach_client, fb_test_employer_phone
) -> User:
    existing_users: dict[str, User] = {
        u.firebase_user_id: u for u in cockroach_client.query(User.get_all)
    }
    if fb_test_employer_id in existing_users:
        return existing_users[fb_test_employer_id]
    # create new
    user = User(
        phone_no=fb_test_employer_phone,
        name="test_user2",
        user_type=UserType.employee,
        firebase_user_id=fb_test_employer_id,
    )
    cockroach_client.query(User.add, items=[user])
    return user


@pytest.fixture(scope="session")
def fast_api_auth_header_employee(fb_test_employee_token):
    return {"Authorization": f"Bearer {fb_test_employee_token}"}
