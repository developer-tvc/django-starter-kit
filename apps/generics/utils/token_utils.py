import jwt
from datetime import datetime, timedelta
from django.conf import settings


def create_password_reset_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "password_reset",
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "password_reset":
            raise ValueError("Invalid token type")

        return payload["user_id"]

    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")

    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
