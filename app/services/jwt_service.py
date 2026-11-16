from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM


# Access Token 유효기간: 60분
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user_id: int) -> str:
    # 현재 UTC 시간
    now = datetime.now(timezone.utc)

    # JWT에 저장할 사용자 정보
    payload = {
        "sub": str(user_id),  # Lenary 사용자 ID
        "iat": now,           # 발급 시간
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )                     # 만료 시간
    }

    # JWT 생성
    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def verify_access_token(token: str) -> int:
    try:
        # JWT 서명과 만료 시간 검증
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]}
        )

        # 검증된 사용자 ID 반환
        return int(payload["sub"])

    except (InvalidTokenError, ValueError, TypeError) as e:
        raise ValueError("유효하지 않은 Access Token입니다.") from e