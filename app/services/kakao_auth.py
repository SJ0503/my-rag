
import httpx

from app.config import KAKAO_APP_ID


TOKEN_INFO_URL = (
    "https://kapi.kakao.com/v1/user/access_token_info"
)

USER_INFO_URL = (
    "https://kapi.kakao.com/v2/user/me"
)


def verify_kakao_token(access_token: str) -> dict:
    """
    Kakao Access Token의 유효성,
    발급 앱, 사용자 ID를 검증한다.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            # 1. 토큰 검증 및 발급 앱 확인
            token_response = client.get(
                TOKEN_INFO_URL,
                headers=headers,
            )

            if token_response.status_code in (400, 401):
                raise ValueError(
                    "유효하지 않은 Kakao 토큰입니다."
                )

            token_response.raise_for_status()
            token_info = token_response.json()

            # 2. 반드시 Lenary의 Kakao 앱에서
            # 발급받은 토큰이어야 한다.
            if token_info.get("app_id") != KAKAO_APP_ID:
                raise ValueError(
                    "다른 Kakao 앱에서 발급된 토큰입니다."
                )

            # 3. 사용자 프로필 조회
            user_response = client.get(
                USER_INFO_URL,
                headers=headers,
            )

            if user_response.status_code in (400, 401):
                raise ValueError(
                    "Kakao 사용자 인증 실패"
                )

            user_response.raise_for_status()
            user_info = user_response.json()

        # 두 API 응답의 사용자 ID가 일치해야 한다.
        user_id = str(user_info.get("id", ""))
        token_user_id = str(token_info.get("id", ""))

        if not user_id or user_id != token_user_id:
            raise ValueError(
                "Kakao 사용자 ID가 일치하지 않습니다."
            )

        properties = user_info.get("properties") or {}
        account = user_info.get("kakao_account") or {}
        profile = account.get("profile") or {}

        nickname = (
            properties.get("nickname")
            or profile.get("nickname")
            or ""
        )

        return {
            "provider_user_id": user_id,
            "name": nickname,
        }

    except httpx.HTTPError as error:
        raise ConnectionError(
            "Kakao 인증 서버 요청에 실패했습니다."
        ) from error
