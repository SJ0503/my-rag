from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError

from app.config import GOOGLE_APPLE_CLIENT_ID


def verify_google_token(token: str) -> dict:
    try:
        # Google ID Token의 서명, 만료 시간, Client ID 검증
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_APPLE_CLIENT_ID
        )

        # 검증된 Google 사용자 정보 반환
        return {
            "provider_user_id": payload["sub"],  # Google 사용자 고유 ID
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified", False),
            "name": payload.get("name"),
            "picture": payload.get("picture")
        }

    # 토큰이 유효하지 않거나 검증 과정에서 오류가 발생한 경우
    except (ValueError, GoogleAuthError) as e:
        raise ValueError("Google ID Token 검증 실패") from e