from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.jwt_service import verify_access_token

from app.services.refresh_service import is_session_active

# HTTP Authorization 헤더에서 Bearer Token 추출
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:

    # 1. 토큰이 없는 경우
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 2. JWT 검증 후 사용자 ID 추출
    try:
        user_id, session_id = verify_access_token(
            credentials.credentials
        )

        if not is_session_active(db, user_id, session_id):
            raise HTTPException(
                status_code=401,
                detail="세션이 만료되었거나 유효하지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"}
            )

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않거나 만료된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 3. MySQL에서 사용자 조회
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="존재하지 않는 사용자입니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 4. 비활성화된 계정인지 확인
    if user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="사용할 수 없는 계정입니다."
        )

    # 5. 인증된 사용자 반환
    return user