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
from src.main import app
from src.db.user import User
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

