from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.schemas.auth import GoogleLoginRequest
from app.services.google_auth import verify_google_token
from app.services.auth_service import login_with_google
from app.dependencies import get_current_user
from app.models.user import User

from app.schemas.auth import (
    GoogleLoginRequest,
    RefreshTokenRequest,
)

from app.services.refresh_service import (
    create_session_tokens,
    rotate_refresh_token,
    revoke_refresh_session,
)

from jwt.exceptions import PyJWKClientError

from app.schemas.auth import AppleLoginRequest
from app.services.apple_auth import verify_apple_token
from app.services.auth_service import login_with_social

from app.schemas.auth import KakaoLoginRequest
from app.services.kakao_auth import verify_kakao_token

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

    # 3. Lenary 자체 토큰 2개 발급
    tokens = create_session_tokens(db=db, user_id=user.user_id)
    
    # 4. JWT 발급 확인 (토큰 원문은 출력하지 않음)
    print("[Backend] 회원 ID:", user.user_id)
    print("[Backend] JWT 발급 여부:", bool(tokens.get("access_token")))

    # 4. 로그인 결과 반환
    return {
        "message": "Google 로그인 성공",
        **tokens,
        "is_new_user": is_new_user,
        "user": {
            "user_id": user.user_id,
            "nickname": user.nickname
        }
    }
    

@router.post("/apple")
def apple_login(
    request: AppleLoginRequest,
    db: Session = Depends(get_db),
):
    # 1. Apple Identity Token 검증
    try:
        apple_user = verify_apple_token(
            request.id_token,
            request.nonce,
        )

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Apple 인증에 실패했습니다.",
        )

    except PyJWKClientError:
        raise HTTPException(
            status_code=503,
            detail="Apple 인증 서버에 연결할 수 없습니다.",
        )

    # 이름은 표시용으로만 사용
    apple_user["name"] = request.name

    # 2. MySQL 회원 조회 및 생성
    try:
        user, is_new_user = login_with_social(
            db,
            "apple",
            apple_user,
        )

    except LookupError:
        raise HTTPException(
            status_code=500,
            detail="Apple 제공자 설정 오류",
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="사용할 수 없는 계정입니다.",
        )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="계정 등록 중 중복이 발생했습니다.",
        )

    # 3. Lenary JWT + Refresh Token 발급
    tokens = create_session_tokens(
        db=db,
        user_id=user.user_id,
    )

    return {
        "message": "Apple 로그인 성공",
        **tokens,
        "is_new_user": is_new_user,
        "user": {
            "user_id": user.user_id,
            "nickname": user.nickname,
        },
    }
    

@router.post("/kakao")
def kakao_login(
    request: KakaoLoginRequest,
    db: Session = Depends(get_db),
):
    try:
        kakao_user = verify_kakao_token(
            request.access_token
        )

    except ValueError as e:
        print("[Kakao 인증 실패]", str(e))

        raise HTTPException(
        status_code=401,
        detail="Kakao 인증에 실패했습니다.",
    )

    except ConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Kakao 인증 서버 요청에 실패했습니다.",
        )

    try:
        user, is_new_user = login_with_social(
            db,
            "kakao",
            kakao_user,
        )

    except LookupError:
        raise HTTPException(
            status_code=500,
            detail="Kakao 제공자 설정 오류",
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="사용할 수 없는 계정입니다.",
        )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="계정 등록 중 중복이 발생했습니다.",
        )

    tokens = create_session_tokens(
        db=db,
        user_id=user.user_id,
    )

    return {
        "message": "Kakao 로그인 성공",
        **tokens,
        "is_new_user": is_new_user,
        "user": {
            "user_id": user.user_id,
            "nickname": user.nickname,
        },
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
    


@router.post("/refresh")
def refresh_tokens(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh Token으로 새 Access/Refresh Token 발급.
    기존 Refresh Token은 즉시 폐기한다.
    """
    return rotate_refresh_token(
        db=db,
        raw_token=request.refresh_token,
    )


@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    전달받은 Refresh Token이 속한
    로그인 세션 전체를 폐기한다.
    """
    revoke_refresh_session(
        db=db,
        raw_token=request.refresh_token,
    )

    return {"message": "로그아웃 완료"}
