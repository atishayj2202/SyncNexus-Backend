import json
import os
import uuid
from uuid import UUID

import firebase_admin
import requests
from firebase_admin import auth, credentials
from pydantic import BaseModel


class FirebaseUser(BaseModel):
    id: str
    email: str
    user_id: UUID


class FirebaseClient:
    env_var = "FIREBASE_SA_KEY_PATH"
    env_var_api_key = "FIREBASE_API_KEY"
    user_key = "user_id"

    def __init__(self):
        try:
            self.app = firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(os.environ.get(self.env_var))
            self.app = firebase_admin.initialize_app(cred)

    def get_user_by_email(self, email: str) -> FirebaseUser | None:
        try:
            user = auth.get_user_by_email(email, app=self.app)
            return FirebaseUser(
                id=user.uid,
                email=user.email,
                user_id=uuid.UUID(user.custom_claims[self.user_key]),
            )
        except auth.UserNotFoundError:
            return None

    def get_user_by_id(self, id: str) -> FirebaseUser | None:
        try:
            user = auth.get_user(id, app=self.app)
            return FirebaseUser(
                id=user.uid,
                email=user.email,
                user_id=uuid.UUID(user.custom_claims[self.user_key]),
            )
        except auth.UserNotFoundError:
            return None

    def get_user_token(self, uid: str):
        token = auth.create_custom_token(uid, app=self.app).decode("utf8")
        api_key = os.environ.get(self.env_var_api_key)
        # URL for Firebase REST API to authenticate with email and password
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"

        # Payload for the authentication request
        payload = {"token": token, "returnSecureToken": True}

        # Make a POST request to authenticate user and get ID token
        response = requests.post(url, data=json.dumps(payload))

        # Check the response
        if response.status_code == 200:
            data = response.json()
            id_token = data["idToken"]
            return id_token
        else:
            return None

    def validate_token(self, id_token) -> str | None:
        decoded_token = auth.verify_id_token(id_token, app=self.app)
        return decoded_token["uid"]

    def create_user_token(self, id: str):
        return auth.create_custom_token(id, app=self.app)

    def create_user(self, email: str, password: str):
        try:
            new_user = auth.create_user(
                email=email,
                email_verified=False,  # Set to True if email is verified
                password=password,
                disabled=False,
                app=self.app,
            )
            return new_user
        except auth.EmailAlreadyExistsError:
            return None

    def delete_user(self, firebase_user_id):
        auth.delete_user(firebase_user_id, self.app)


if __name__ == "__main__":
    client = FirebaseClient()
    print(client.get_user_token("vQ0LNIqBZGfTX6Ttoy6INrSiNlc2"))
