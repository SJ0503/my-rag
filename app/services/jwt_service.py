
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM


# Access Token 유효기간: 15분
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def create_access_token(
    user_id: int,
    session_id: str,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "token_use": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def verify_access_token(token: str) -> tuple[int, str]:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "sid",
                    "token_use",
                    "exp",
                ]
            },
        )

        if payload.get("token_use") != "access":
            raise ValueError("Access Token이 아닙니다.")

        user_id = int(payload["sub"])
        session_id = payload["sid"]

        if (
            user_id <= 0
            or not isinstance(session_id, str)
            or not session_id
        ):
            raise ValueError("잘못된 토큰 정보입니다.")

        return user_id, session_id

    except (InvalidTokenError, ValueError, TypeError, KeyError) as e:
        raise ValueError(
            "유효하지 않은 Access Token입니다."
        ) from e
