from fastapi import APIRouter, HTTPException

from app.schemas.auth import GoogleLoginRequest
from app.services.google_auth import verify_google_token


# 인증 관련 API 라우터
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Google 로그인 API
@router.post("/google")
def google_login(request: GoogleLoginRequest):

    try:
        # Google ID Token 검증 및 사용자 정보 조회
        user_info = verify_google_token(request.id_token)

        # 검증 성공 시 사용자 정보 반환
        return {
            "message": "Google 토큰 검증 성공",
            "user": user_info
        }

    except ValueError:
        # 유효하지 않은 토큰이면 401 반환
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 Google 인증 토큰입니다."
        )