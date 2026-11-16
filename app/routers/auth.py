from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.schemas.auth import GoogleLoginRequest
from app.services.google_auth import verify_google_token
from app.services.auth_service import login_with_google
from app.services.jwt_service import create_access_token
from app.dependencies import get_current_user
from app.models.user import User

# 인증 관련 API Router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/google")
def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    # 1. Google ID Token 검증
    try:
        google_user = verify_google_token(request.id_token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 Google 인증 토큰입니다."
        )

    # 2. MySQL 회원 조회 또는 신규 생성
    try:
        user, is_new_user = login_with_google(db, google_user)

    except LookupError:
        raise HTTPException(
            status_code=500,
            detail="Google 제공자 설정 오류"
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="사용할 수 없는 계정입니다."
        )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="소셜 계정 등록 중 중복이 발생했습니다."
        )

    # 3. Lenary 자체 Access Token 발급
    access_token = create_access_token(user.user_id)

    # 4. 로그인 결과 반환
    return {
        "message": "Google 로그인 성공",
        "access_token": access_token,
        "token_type": "bearer",
        "is_new_user": is_new_user,
        "user": {
            "user_id": user.user_id,
            "nickname": user.nickname
        }
    }

# 현재 로그인한 사용자 정보 조회
@router.get("/me")
def get_my_info(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.user_id,
        "nickname": current_user.nickname,
        "role": current_user.role,
        "status": current_user.status
    }