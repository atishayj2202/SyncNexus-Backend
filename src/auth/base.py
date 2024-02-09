from fastapi import Header, HTTPException
from firebase_admin import auth

from src.client.cockroach import CockroachDBClient
from src.client.firebase import FirebaseClient
from src.db.tables.user import User


def _get_requesting_user(
    authorization, cockroach_client: CockroachDBClient, firebase_client: FirebaseClient
) -> User:
    firebase_user_id = get_user_from_token(firebase_client, authorization)
    user = cockroach_client.query(
        User.get_by_field_unique,
        field="firebase_user_id",
        match_value=firebase_user_id,
        error_not_exist=False,
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_from_token(
    firebase_client: FirebaseClient(), authorization: str = Header(...)
) -> str:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401, detail="Invalid authentication scheme. Use Bearer."
            )
        return firebase_client.validate_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Expired ID token")
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Revoked ID token")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
