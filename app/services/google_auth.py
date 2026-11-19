from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError

from app.config import GOOGLE_WEB_CLIENT_ID


def verify_google_token(token: str) -> dict:
    try:
        # Google ID Token 검증
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_WEB_CLIENT_ID,
        )

        return {
            "provider_user_id": payload["sub"],
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified", False),
            "name": payload.get("name"),
            "picture": payload.get("picture"),
        }

    except (ValueError, GoogleAuthError) as e:
        # 개발 환경에서만 검증 실패 원인 확인
        print("Google 토큰 검증 실패:", type(e).__name__, str(e))

        raise ValueError(
            "유효하지 않은 Google 인증 토큰입니다."
        ) from e